# Initial Copyright (c)2022 5@xes
# Calibration Shapes Reborn version Copyright Slashee the Cow 2025

from . import CalibrationShapesReborn

def getMetaData():
    return {}

def register(app):
    return {"extension": CalibrationShapesReborn.CalibrationShapesReborn()}
