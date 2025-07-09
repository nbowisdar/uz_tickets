from datetime import datetime

import pytz
from pydantic import BaseModel


def to_human_time(timestamp: int) -> str:
    # Convert to datetime object in UTC
    dt_object = datetime.fromtimestamp(timestamp, tz=pytz.UTC)

    # Convert to Ukrainian time (EET, UTC+2)
    ukraine_tz = pytz.timezone("Europe/Kiev")
    dt_ukraine = dt_object.astimezone(ukraine_tz)

    # Format the datetime to desired string format
    formatted_date = dt_ukraine.strftime("%d.%m.%Y at %H:%M")

    return formatted_date


class _Time(BaseModel):
    station_from: str
    station_to: str


class WagonClass(BaseModel):
    name: str
    free_seats: int
    price: int

    def show_message(self) -> str:
        msg = f"""
Клас: {self.name}
Всього вільних місць: {self.free_seats}  
Ціна: {self.price // 100} грн
        """
        return msg


class Train(_Time):
    id: int
    number: str
    wagon_classes: list[WagonClass]

    @property
    def total_free_seats(self) -> int:
        total = 0
        for wc in self.wagon_classes:
            total += wc.free_seats
        return total

    def show_message(self) -> str:
        msg = f"""
Потяг {self.number}
Всього вільних місць: {self.total_free_seats}
        """
        if self.total_free_seats > 0:
            for wg in self.wagon_classes:
                msg += wg.show_message()
        return msg


class Direct(_Time):
    id: int
    depart_at: int
    arrive_at: int
    station_from: str
    station_to: str
    train: Train

    def show_message(self) -> str:
        msg = f"""
Відправлення: {self.depart_at_human}
Прибуття: {self.arrive_at_human} 
"""
        msg += self.train.show_message()
        return msg

    @property
    def depart_at_human(self):
        return to_human_time(self.depart_at)

    @property
    def arrive_at_human(self):
        return to_human_time(self.arrive_at)


class Transfer(BaseModel):
    station_from: str
    station_to: str
    direct: list[Direct]
    # with_transfer: str
    # monitoring: str

    def show_message(self, with_free_seats=True) -> str:
        msg = f"""
Станція відправлення: {self.station_from}
Станція прибуття: {self.station_to}
Всього потягів: {len(self.direct)}
"""
        for d in self.direct:
            if with_free_seats and d.train.total_free_seats > 0:
                msg += d.show_message()
            else:
                msg += d.show_message()
        return msg
