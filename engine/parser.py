import argparse
import uuid
from .files import validate_file
from .agent import supported_languages

supported_languages_extensions = supported_languages.keys()

parser = argparse.ArgumentParser(description="Tilecraft Game Engine")
parser.add_argument("--agent1", help="Path to Agent 1 script", type=validate_file(supported_languages_extensions))
parser.add_argument("--agent2", help="Path to Agent 2 script", type=validate_file(supported_languages_extensions))
parser.add_argument("--map", default="maps/map1.csv", help="Path to map file (.csv)", type=validate_file("csv"))
parser.add_argument("--id", default=uuid.uuid4(), help="Game id")

def get_args() -> dict[str,str]:
    args = parser.parse_args()
    return {
        "game_id" : args.id,
        "map" : args.map,
        "agent1" : args.agent1,
        "agent2" : args.agent2
    }