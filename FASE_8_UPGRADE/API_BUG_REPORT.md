# API Bug Report - Critical Content Field Issue

**Date:** October 27, 2025
**Severity:** High
**Status:** Documented
**Discovered by:** NEXUS (during DMR benchmark Session 1)
**Episode ID:** `27cbc7b2-11d4-4c1e-b972-d864428b5532`

---

## Summary

The `/memory/action` endpoint **ignores the `content` field** when a custom `action_type` is provided, using the `action_type` value as content instead.

---

## Impact

**Severity: HIGH**
- Affects ALL users of the `/memory/action` API endpoint
- Causes data loss: intended content is discarded
- Results in meaningless memory entries (content = action_type string)
- Discovered during DMR benchmark (caused 0% accuracy until fixed)

---

## Reproduction Steps

1. Call `/memory/action` with custom action_type:

```bash
curl -X POST http://localhost:8003/memory/action \
  -H "Content-Type: application/json" \
  -d '{
    "action_type": "test",
    "content": "This is the actual content I want to save",
    "tags": ["test"],
    "importance": 0.8
  }'
```

2. Check database:

```sql
SELECT episode_id, content
FROM nexus_memory.zep_episodic_memory
WHERE 'test' = ANY(tags);
```

**Expected:** `content = "This is the actual content I want to save"`
**Actual:** `content = "test"` (the action_type value)

---

## Root Cause

File: `/mnt/d/01_PROYECTOS_ACTIVOS/CEREBRO_MASTER_NEXUS_001/FASE_4_CONSTRUCCION/src/api/main.py`
Lines: 379-398

```python
@app.post("/memory/action", response_model=MemoryActionResponse)
async def memory_action(request: MemoryActionRequest):
    # ...

    # BUG: Uses action_type as content fallback
    if "content" in request.action_details:
        content = request.action_details["content"]
    elif request.action_details:
        content = json_module.dumps(request.action_details, indent=2, default=str)
    else:
        content = request.action_type  # ← FALLBACK uses action_type
```

**Problem:** The API expects content in `action_details.content`, NOT as a top-level `content` field.

**Current behavior:**
- User sends: `{"action_type": "test", "content": "..."}`
- API receives: `request.action_details = {}` (content not in action_details)
- API falls through to: `content = request.action_type`
- Result: Saves "test" instead of actual content

---

## Workaround (Temporary Fix for Users)

Put content inside `action_details`:

```python
# WRONG (current user pattern):
payload = {
    "action_type": "memory",
    "content": "Actual content here",
    "tags": ["test"]
}

# CORRECT (workaround):
payload = {
    "action_type": "memory",
    "action_details": {
        "content": "Actual content here"
    },
    "tags": ["test"]
}
```

---

## Proposed Solutions

### Option A: Accept Top-Level Content Field (Recommended)

Modify API to check top-level `content` first:

```python
@app.post("/memory/action", response_model=MemoryActionResponse)
async def memory_action(request: MemoryActionRequest):
    # Check top-level content field first (NEW)
    if hasattr(request, 'content') and request.content:
        content = request.content
    # Then check action_details.content (existing)
    elif "content" in request.action_details:
        content = request.action_details["content"]
    elif request.action_details:
        content = json_module.dumps(request.action_details, indent=2, default=str)
    else:
        content = request.action_type
```

**Also update Pydantic model:**

```python
class MemoryActionRequest(BaseModel):
    action_type: str = Field(..., description="Type of action to perform")
    content: Optional[str] = Field(None, description="Content to store")  # NEW
    action_details: Dict[str, Any] = Field(default_factory=dict)
    context_state: Optional[Dict[str, Any]] = Field(default_factory=dict)
    tags: Optional[List[str]] = Field(default_factory=list)
```

**Pros:**
- More intuitive API (content at top-level makes sense)
- Backward compatible (checks action_details.content as fallback)
- Matches user expectations

**Cons:**
- Changes API contract (minor)

---

### Option B: Document Current Behavior Only

Keep current behavior, but:
1. Update API documentation to clarify content must be in action_details
2. Add examples showing correct usage
3. Consider deprecation warning for missing content

**Pros:**
- No code changes
- Keeps existing behavior

**Cons:**
- Unintuitive API design
- Users will continue to make this mistake

---

## Recommendation

**Implement Option A** for better UX and fewer user errors.

---

## Testing

After fix, verify with DMR benchmark:

```bash
cd /mnt/d/01_PROYECTOS_ACTIVOS/CEREBRO_MASTER_NEXUS_001/FASE_8_UPGRADE/benchmarks/dmr
python3 dmr_benchmark_api_only.py
```

Should achieve 100% accuracy (as currently does with workaround).

---

## Related Files

- **Bug Report:** This file
- **API Code:** `FASE_4_CONSTRUCCION/src/api/main.py:379-398`
- **DMR Benchmark:** `FASE_8_UPGRADE/benchmarks/dmr/dmr_benchmark_api_only.py`
- **TRACKING:** `FASE_8_UPGRADE/TRACKING.md` (Bug #1)

---

## Status

- [x] Bug discovered (Oct 27, 2025)
- [x] Documented in TRACKING.md
- [x] Documented in this report
- [x] Workaround implemented in DMR benchmark
- [ ] Fix applied to API code
- [ ] Tests updated
- [ ] Documentation updated
- [ ] Users notified of breaking change (if any)

---

**Report generated:** October 27, 2025
**By:** NEXUS Autonomous Analysis
**Session:** FASE_8_UPGRADE Session 1
