from enum import Enum


class ResultType(str, Enum):
    SR = "SR"
    T2I = "T2I"
    I2I = "I2I"
    INP = "INP"
    EXP = "EXP"
    SEG = "SEG"
    COL = "COL"
    FR = "FR"