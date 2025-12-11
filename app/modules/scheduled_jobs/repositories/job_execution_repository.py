"""
Repository untuk operasi database JobExecution.
"""

from typing import Optional, List
from datetime import datetime, timedelta
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.scheduled_jobs.models.job_execution import JobExecution


class JobExecutionRepository:
    """Repository untuk operasi database job execution logs"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, job_execution: JobExecution) -> JobExecution:
        """Simpan job execution log baru"""
        self.db.add(job_execution)
        await self.db.commit()
        await self.db.refresh(job_execution)
        return job_execution

    async def get_by_id(self, execution_id: int) -> Optional[JobExecution]:
        """Ambil job execution berdasarkan ID"""
        result = await self.db.execute(
            select(JobExecution).where(JobExecution.id == execution_id)
        )
        return result.scalar_one_or_none()

    async def get_latest_by_job_id(self, job_id: str) -> Optional[JobExecution]:
        """Ambil execution log terakhir dari suatu job"""
        result = await self.db.execute(
            select(JobExecution)
            .where(JobExecution.job_id == job_id)
            .order_by(desc(JobExecution.started_at))
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def list_by_job_id(
        self,
        job_id: str,
        limit: int = 50,
        offset: int = 0
    ) -> List[JobExecution]:
        """List execution logs untuk suatu job dengan pagination"""
        result = await self.db.execute(
            select(JobExecution)
            .where(JobExecution.job_id == job_id)
            .order_by(desc(JobExecution.started_at))
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())

    async def count_by_job_id(self, job_id: str) -> int:
        """Hitung total execution logs untuk suatu job"""
        result = await self.db.execute(
            select(func.count(JobExecution.id))
            .where(JobExecution.job_id == job_id)
        )
        return result.scalar_one()

    async def list_recent(
        self,
        hours: int = 24,
        limit: int = 100
    ) -> List[JobExecution]:
        """List execution logs terbaru dalam X jam terakhir"""
        since = datetime.now() - timedelta(hours=hours)
        result = await self.db.execute(
            select(JobExecution)
            .where(JobExecution.started_at >= since)
            .order_by(desc(JobExecution.started_at))
            .limit(limit)
        )
        return list(result.scalars().all())

    async def count_failed_executions(
        self,
        job_id: Optional[str] = None,
        hours: int = 24
    ) -> int:
        """Hitung execution yang gagal dalam X jam terakhir"""
        since = datetime.now() - timedelta(hours=hours)
        query = select(func.count(JobExecution.id)).where(
            JobExecution.success == False,
            JobExecution.started_at >= since
        )
        
        if job_id:
            query = query.where(JobExecution.job_id == job_id)
        
        result = await self.db.execute(query)
        return result.scalar_one()

    async def cleanup_old_logs(self, days: int = 30) -> int:
        """
        Hapus execution logs yang lebih lama dari X hari.
        
        Returns:
            Jumlah row yang dihapus
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        result = await self.db.execute(
            select(JobExecution).where(JobExecution.created_at < cutoff_date)
        )
        old_logs = result.scalars().all()
        
        for log in old_logs:
            await self.db.delete(log)
        
        await self.db.commit()
        return len(old_logs)
