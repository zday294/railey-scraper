# cabin.py
from dataclasses import dataclass, asdict
from os import name
from typing import Optional, List, Any, Dict
import json


@dataclass
class rcav:
    begin: str
    end: str
    adult: str
    child: str

    @classmethod
    def from_dict(cls, d: Dict) -> "rcav":
        return cls(
            begin=d.get("begin"),
            end=d.get("end"),
            adult=d.get("adult"),
            child=d.get("child"),
        )


@dataclass
class qp:
    rcav: rcav
    eid: int

    @classmethod
    def from_dict(cls, d: Dict) -> "qp":
        rcav_data = d.get("rcav", {})
        return cls(
            rcav=rcav.from_dict(rcav_data),
            eid=d.get("eid"),
        )


@dataclass
class Price:
    eid: int
    p: float
    c: str
    n: str
    qp: Optional[qp]
    do: Optional[Any] = None
    qo: Optional[Any] = None
    dn: Optional[Any] = None
    dd: Optional[Any] = None
    bt: Optional[int] = None
    et: Optional[int] = None
    b: Optional[str] = None
    e: Optional[str] = None
    force_call_to_book: Optional[bool] = False

    @classmethod
    def from_dict(cls, d: Dict) -> "Price":
        qp_data = d.get("qp")
        return cls(
            eid=d.get("eid"),
            p=d.get("p"),
            c=d.get("c"),
            n=d.get("n"),
            qp=qp.from_dict(qp_data) if qp_data is not None else None,
            do=d.get("do"),
            qo=d.get("qo"),
            dn=d.get("dn"),
            dd=d.get("dd"),
            bt=d.get("bt"),
            et=d.get("et"),
            b=d.get("b"),
            e=d.get("e"),
            force_call_to_book=d.get("force_call_to_book", False),
        )


@dataclass
class Cabin:
    eid: int
    name: str
    prices: List[Price]
    type: int

    @classmethod
    def from_dict(cls, d: Dict) -> "Cabin":
        prices_data = d.get("prices", [])
        prices_objs = [Price.from_dict(p) for p in prices_data]
        return cls(
            eid=d.get("eid"),
            name=d.get("name"),
            prices=prices_objs,
            type=d.get("type"),
        )

    def to_dict(self) -> Dict:
        # asdict will convert nested dataclasses to dictionaries
        return asdict(self)

    def get_price(self) -> Optional[float]:
        if not self.prices:
            return None
        return self.prices[0].p

    @classmethod
    def from_json(cls, s: str) -> "Cabin":
        return cls.from_dict(json.loads(s))

    def to_json(self, **kwargs) -> str:
        return json.dumps(self.to_dict(), **kwargs)

    # allow sorting by name (case-insensitive); return NotImplemented for other types
    def __lt__(self, other: "Cabin") -> bool:
        if not isinstance(other, Cabin):
            return NotImplemented
        return (self.name or "").lower() < (other.name or "").lower()

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Cabin):
            return NotImplemented
        return (self.name or "").lower() == (other.name or "").lower()
    

class KeyCabin:
    def __init__(self, name: str, occupancy: str, beds: int, baths: int, url: str, price=0.0):
        self.name = name
        self.occupancy = occupancy
        self.beds = beds
        self.baths = baths
        self.price = price
        self.url = url

    def __repr__(self):
        return (
            f"Cabin: {self.name}\n"
            f"Beds: {self.beds}\n"
            f"Baths: {self.baths}\n"
            f"Occupancy: {self.occupancy}\n"
            f"Price: ${self.price:.2f}"
        )
    
    def get_price(self) -> Optional[float]:
        return self.price