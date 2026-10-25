"""Assemble the report page: template.html + payload.b64 -> replay_hides_the_habit.html"""
import os
H = os.path.dirname(os.path.abspath(__file__))
t = open(f"{H}/template.html").read().replace("__PAYLOAD__", open(f"{H}/payload.b64").read())
open(f"{H}/replay_hides_the_habit.html", "w").write(t)
print(f"{len(t) / 1e6:.1f} MB")
