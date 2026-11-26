"""Rebuild the gripper from local STEP definitions and occurrence placements.

Run with a Python interpreter that can import FreeCAD 1.1, Part and Import.
"""
import json
from pathlib import Path

import FreeCAD as App
import Import
import Part

ROOT = Path(__file__).resolve().parents[1]
CAD = ROOT / "cad"
GROUPS = {
    "Wrist": "Wrist interface and motor",
    "Frame": "Rail frame and pinion",
    "Left": "Left carriage and finger",
    "Right": "Right carriage and finger",
}


def build():
    layout = json.loads((CAD / "layout.json").read_text(encoding="utf-8"))
    doc = App.newDocument("B601CustomGripper")
    root = doc.addObject("App::Part", "Gripper")
    root.Label = "B601-DM custom gripper"
    shapes = {}
    for group, rows in layout.items():
        assembly = doc.addObject("App::Part", group)
        assembly.Label = GROUPS[group]
        root.addObject(assembly)
        for index, row in enumerate(rows, 1):
            part = row["part"]
            if part not in shapes:
                shapes[part] = Part.read(str(CAD / (part + ".step")))
            shape = shapes[part].copy()
            pose = App.Placement(App.Vector(*row["xyz"]), App.Rotation(*row["quat"]))
            shape.Placement = pose * shape.Placement
            obj = doc.addObject("Part::Feature", f"{group}_{index:02}")
            obj.Label = f"{Path(part).name} [{group} {index:02}]"
            obj.Shape = shape
            obj.addProperty("App::PropertyString", "SourceFile", "Source")
            obj.SourceFile = f"cad/{part}.step"
            assembly.addObject(obj)
    doc.recompute()
    return doc, root


if __name__ == "__main__":
    document, gripper = build()
    document.saveAs(str(CAD / "gripper.FCStd"))
    Import.export([gripper], str(CAD / "gripper.step"))
