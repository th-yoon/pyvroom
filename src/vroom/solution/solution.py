"""The computed solutions."""
from typing import Any, Dict, Union
from pathlib import Path
import io
import json
from contextlib import redirect_stdout

import numpy
import pandas

from .. import _vroom

NA_SUBSTITUTE = 4293967297


class Solution(_vroom.Solution):
    """
    The computed solutions.

    Attributes:
        routes:
            Frame outlining all routes for all vehicles.
    """

    @property
    def routes(self) -> pandas.DataFrame:
        """
        Frame outlining all routes for all vehicles.

        It includes the following columns.

        vehicle_id:
            Id of the vehicle assigned to this route.
        type:
            The activity the vehicle is performing. The available
            categories are `start`, `end`, `break`, `job`, `delivery`
            and `pickup`.
        arrival:
            Timepoint when the actvity ends.
        duration:
            The length of the activity.
        setup:
            Total setup time for this route.
        service:
            Total service time for this route.
        waiting_time:
            Total waiting time for this route.
        location_index:
            The index for the location of the destination.
        longitude:
            If available, the longitude of the destination.
        latitude:
            If available, the latitude of the destination.
        id:
            The identifier for the task that was performed.
        description:
            Text description provided to this step.
        """
        array = numpy.asarray(self._routes_numpy())
        frame = pandas.DataFrame(
            {
                "vehicle_id": array["vehicle_id"],
                "type": pandas.Categorical(
                    array["type"].astype("U9"),
                    categories=["start", "end", "break", "job", "delivery", "pickup"],
                ),
                "arrival": array["arrival"],
                "duration": array["duration"],
                "setup": array["setup"],
                "service": array["service"],
                "waiting_time": array["waiting_time"],
                "location_index": array["location_index"],
                "longitude": pandas.array(array["longitude"], dtype="Int64"),
                "latitude": pandas.array(array["latitude"], dtype="Int64"),
                "id": pandas.array(array["id"], dtype="Int64"),
                "description": array["description"].astype("U40"),
            }
        )
        for column in ["longitude", "latitude", "id"]:
            if (frame[column] == NA_SUBSTITUTE).all():
                del frame[column]
            else:
                frame.loc[frame[column] == NA_SUBSTITUTE, column] = pandas.NA
        return frame

    def to_dict(self) -> Dict[str, Any]:
        """Convert solution into VROOM compatible dictionary."""
        stream = io.StringIO()
        with redirect_stdout(stream):
            self._solution_json()
        return json.loads(stream.getvalue())

    def to_json(self, filepath: Union[str, Path]) -> None:
        """Store solution into VROOM compatible JSON file."""
        with open(filepath, "w") as handler:
            with redirect_stdout(handler):
                self._solution_json()
