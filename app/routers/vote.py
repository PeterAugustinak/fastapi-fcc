from typing import List, Optional

from fastapi import Response, status, Depends, APIRouter, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc

from .. import schemas
from .. import oauth2
from .. import models
from ..database import get_db
from ..utils import record_not_exist, create, vote_conflict

router = APIRouter(prefix="/vote", tags=["Vote"])


@router.post("/", status_code=status.HTTP_201_CREATED)
def vote(vote: schemas.Vote, db: Session = Depends(get_db),
         current_user: int = Depends(oauth2.get_current_user)):

    vote_query = db.query(models.Vote).filter(
        models.Vote.post_id == vote.post_id,
        models.Vote.user_id == current_user.id
    )
    found_vote = vote_query.first()

    if vote.dir == 1:
        if found_vote:
            message = f"User {current_user.id} already voted for post " \
                      f"{vote.post_id}"
            vote_conflict(message)

        create_obj = {"post_id": vote.post_id, "user_id": current_user.id}
        create(create_obj, models.Vote, db)

        return {"message": "successfully added vote"}

    else:
        if not found_vote:
            record_not_exist("Vote", -1)

        vote_query.delete(synchronize_session=False)
        db.commit()

        return {"message": "vote successfully deleted"}
