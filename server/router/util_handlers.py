from fastapi import APIRouter

from schema import Action

router = APIRouter(
    tags=["Util"],
)


@router.get("/action.json", operation_id="get_action_json_schema")
async def get_action_json_schema() -> str:
    return Action.schema_json()
