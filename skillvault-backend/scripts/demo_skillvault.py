import asyncio
import json
import os
import sys

# Ensure backend root is on PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from app.api.deps import get_llm_provider
from app.db.base import Base
from app.db.repositories.execution_repository import ExecutionRepository
from app.db.repositories.skill_repository import SkillRepository
from app.db.repositories.task_repository import TaskRepository
from app.services.embedding_service import EmbeddingService
from app.services.execution_service import ExecutionService
from app.services.generation_service import GenerationService
from app.services.retrieval_service import RetrievalService
from app.services.skill_metrics_service import SkillMetricsService
from app.services.skill_service import SkillService
from app.services.task_service import TaskService
from app.skills.executor import LocalSkillExecutor
from app.core.config import settings


async def run_demo():
    print("=" * 80)
    print("           SKILLVAULT BACKEND END-TO-END DEMO EXECUTION           ")
    print("=" * 80)

    print("\n[Step 1] Initializing Database Schema & Seeding Vault Built-in Skills...")
    
    demo_db_file = "skillvault_demo.db"
    demo_db_url = settings.DATABASE_URL
    if demo_db_url.startswith("postgresql://"):
        demo_db_url = demo_db_url.replace("postgresql://", "postgresql+asyncpg://", 1)

    try:
        engine = create_async_engine(demo_db_url, echo=False)
        async with engine.connect() as conn:
            try:
                await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
                await conn.commit()
            except Exception:
                pass
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    except Exception as e:
        print(f"PostgreSQL connection notice ({e}). Using local SQLite demo database.")
        demo_db_url = "sqlite+aiosqlite:///skillvault_demo.db"
        engine = create_async_engine(
            demo_db_url,
            echo=False,
            connect_args={"timeout": 30},
        )
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    DemoSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    try:
        async with DemoSessionLocal() as session:
            llm = get_llm_provider()

            task_repo = TaskRepository(session)
            skill_repo = SkillRepository(session)
            exec_repo = ExecutionRepository(session)

            emb_service = EmbeddingService(llm)
            gen_service = GenerationService(llm)
            ret_service = RetrievalService(skill_repo, emb_service)
            skill_service = SkillService(skill_repo, emb_service)
            metrics_service = SkillMetricsService(skill_repo)
            exec_service = ExecutionService(exec_repo, metrics_service, LocalSkillExecutor())

            task_service = TaskService(
                task_repo=task_repo,
                execution_repo=exec_repo,
                generation_service=gen_service,
                retrieval_service=ret_service,
                skill_service=skill_service,
                execution_service=exec_service,
            )

            # Seed initial capabilities
            await skill_service.seed_builtin_skills()
            initial_skills, initial_count = await skill_service.list_skills(limit=100)
            print(f"Vault Skill Inventory: {initial_count} Skills Registered & ACTIVE.")

            # --- DEMO 1: CSV Employee Salary Analysis ---
            print("\n" + "-" * 80)
            print("DEMO 1: Task — 'Analyze employees.csv and calculate average salary.'")
            print("-" * 80)
            res1 = await task_service.create_and_execute_task(
                "Analyze employees.csv and calculate average salary."
            )
            print(f"-> Task ID: {res1.task_id}")
            print(f"-> Selected Strategy: {res1.strategy.upper()}")
            print(f"-> Selected Skill: {res1.skill.get('name') if res1.skill else 'None'}")
            print(f"-> Execution Status: {res1.status.upper()}")
            print(f"-> Output Summary: {json.dumps(res1.result, indent=2)}")

            # --- DEMO 2: Sales Revenue Analysis ---
            print("\n" + "-" * 80)
            print("DEMO 2: Task — 'Which salesperson generated the highest revenue?'")
            print("-" * 80)
            res2 = await task_service.create_and_execute_task(
                "Which salesperson generated the highest revenue?"
            )
            print(f"-> Task ID: {res2.task_id}")
            print(f"-> Selected Strategy: {res2.strategy.upper()}")
            print(f"-> Selected Skill: {res2.skill.get('name') if res2.skill else 'None'}")
            print(f"-> Execution Status: {res2.status.upper()}")
            print(f"-> Top Salesperson Result: {json.dumps(res2.result.get('top_salesperson') if res2.result else {}, indent=2)}")

            # --- DEMO 3: Products JSON Filtering ---
            print("\n" + "-" * 80)
            print("DEMO 3: Task — 'Find products with rating above 4.5.'")
            print("-" * 80)
            res3 = await task_service.create_and_execute_task(
                "Find products with rating above 4.5."
            )
            print(f"-> Task ID: {res3.task_id}")
            print(f"-> Selected Strategy: {res3.strategy.upper()}")
            print(f"-> Selected Skill: {res3.skill.get('name') if res3.skill else 'None'}")
            print(f"-> Execution Status: {res3.status.upper()}")
            print(f"-> Total Matching Products: {res3.result.get('matching_records') if res3.result else 0}")

            # --- DEMO 4: Skill Reuse Loop Test (Same task submitted again) ---
            print("\n" + "-" * 80)
            print("DEMO 4: REUSE LOOP TEST — Re-submitting Demo 1 task: 'Analyze employees.csv and calculate average salary.'")
            print("-" * 80)
            res4 = await task_service.create_and_execute_task(
                "Analyze employees.csv and calculate average salary."
            )
            print(f"-> Task ID: {res4.task_id}")
            print(f"-> Strategy Selected: {res4.strategy.upper()}")
            print(f"-> Selected Skill: {res4.skill.get('name') if res4.skill else 'None'}")
            
            # Verify Skill Metrics
            csv_skill = await skill_repo.get_by_slug("csv-analyzer")
            if csv_skill:
                print(f"-> 'CSV Analyzer' Skill Stats in DB — Usage Count: {csv_skill.usage_count}, Success Count: {csv_skill.success_count}, Last Used At: {csv_skill.last_used_at}")

            # --- DEMO 5: Missing Capability & Untrusted Code Security Boundary Test ---
            print("\n" + "-" * 80)
            print("DEMO 5: MISSING CAPABILITY TEST — 'Convert employees.csv into a polished HTML report containing charts.'")
            print("-" * 80)
            res5 = await task_service.create_and_execute_task(
                "Convert employees.csv into a polished HTML report containing charts."
            )
            print(f"-> Task ID: {res5.task_id}")
            print(f"-> Selected Strategy: {res5.strategy.upper()}")
            print(f"-> Execution Status: {res5.execution.get('status') if res5.execution else 'None'}")
            print(f"-> Security Notice: {res5.result.get('notice') if res5.result else ''}")

            print("\n" + "=" * 80)
            print("                  DEMO EXECUTION COMPLETED SUCCESSFULLY                  ")
            print("=" * 80)

    finally:
        await engine.dispose()
        if os.path.exists(demo_db_file):
            try:
                os.remove(demo_db_file)
            except Exception:
                pass


if __name__ == "__main__":
    asyncio.run(run_demo())
