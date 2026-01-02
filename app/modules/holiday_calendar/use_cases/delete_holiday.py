"""Use case untuk delete holiday."""

from app.modules.holiday_calendar.repositories import HolidayQueries, HolidayCommands
from app.core.exceptions import NotFoundException


class DeleteHolidayUseCase:
    """Use case untuk delete holiday."""

    def __init__(self, queries: HolidayQueries, commands: HolidayCommands):
        self.queries = queries
        self.commands = commands

    async def execute(self, holiday_id: int) -> None:
        """Hapus holiday.
        
        Args:
            holiday_id: ID holiday yang akan dihapus
            
        Raises:
            NotFoundException: Jika holiday tidak ditemukan
        """
        holiday = await self.queries.get_by_id(holiday_id)
        if not holiday:
            raise NotFoundException(f"Holiday dengan ID {holiday_id} tidak ditemukan")

        await self.commands.delete(holiday)
