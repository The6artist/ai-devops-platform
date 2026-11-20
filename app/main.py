
from pathlib import Path
from contextlib import contextmanager
import sqlite3
from typing import Literal

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel


app = FastAPI(
    title="Vice City Game Server",
    description="A simulated multiplayer game server for DevOps learning",
    version="2.0.0"
)


# Database file location: project-root/players.db

BASE_DIR = Path(__file__).resolve().parent.parent
DATABASE_PATH = BASE_DIR / "players.db"


# Database connection manager

@contextmanager
def get_db():
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row

    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


# Create the players table if it does not exist

def initialize_database():
    with get_db() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS players (
                player_id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                location TEXT NOT NULL DEFAULT 'Vice City',
                status TEXT NOT NULL DEFAULT 'online'
            )
        """)


initialize_database()


# Request models

class Player(BaseModel):
    username: str


class PlayerStatus(BaseModel):
    status: Literal["online", "offline"]


# 1. Health check

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "application": "Vice City Game Server"
    }


# 2. Register a player

@app.post("/players", status_code=201)
def create_player(player: Player):

    with get_db() as connection:

        cursor = connection.execute(
            """
            INSERT INTO players (username)
            VALUES (?)
            """,
            (player.username,)
        )

        new_player = connection.execute(
            "SELECT * FROM players WHERE player_id = ?",
            (cursor.lastrowid,)
        ).fetchone()

        return dict(new_player)


# 3. Get all players

@app.get("/players")
def get_players():

    with get_db() as connection:

        result = connection.execute(
            "SELECT * FROM players ORDER BY player_id"
        ).fetchall()

        return [dict(player) for player in result]


# 4. Get one player

@app.get("/players/{player_id}")
def get_player(player_id: int):

    with get_db() as connection:

        player = connection.execute(
            "SELECT * FROM players WHERE player_id = ?",
            (player_id,)
        ).fetchone()

        if player is None:
            raise HTTPException(
                status_code=404,
                detail="Player not found"
            )

        return dict(player)


# 5. Delete a player

@app.delete("/players/{player_id}")
def delete_player(player_id: int):

    with get_db() as connection:

        player = connection.execute(
            "SELECT * FROM players WHERE player_id = ?",
            (player_id,)
        ).fetchone()

        if player is None:
            raise HTTPException(
                status_code=404,
                detail="Player not found"
            )

        connection.execute(
            "DELETE FROM players WHERE player_id = ?",
            (player_id,)
        )

        return {
            "message": "Player removed successfully",
            "player": dict(player)
        }


# 6. Update player status

@app.put("/players/{player_id}")
def update_player_status(
    player_id: int,
    player_status: PlayerStatus
):

    with get_db() as connection:

        player = connection.execute(
            "SELECT * FROM players WHERE player_id = ?",
            (player_id,)
        ).fetchone()

        if player is None:
            raise HTTPException(
                status_code=404,
                detail="Player not found"
            )

        connection.execute(
            """
            UPDATE players
            SET status = ?
            WHERE player_id = ?
            """,
            (player_status.status, player_id)
        )

        updated_player = connection.execute(
            "SELECT * FROM players WHERE player_id = ?",
            (player_id,)
        ).fetchone()

        return {
            "message": "Player status updated",
            "player": dict(updated_player)
        }
