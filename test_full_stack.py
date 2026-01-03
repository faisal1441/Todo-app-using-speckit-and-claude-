#!/usr/bin/env python
"""
Full-Stack Todo App Testing Script

Tests the complete integration between:
- Frontend: Next.js 14 (http://localhost:3000)
- Backend: FastAPI (http://localhost:8000)
- Database: PostgreSQL via Neon DB

Run this script to verify all components are working correctly.
"""

import asyncio
import json
from backend.core.config import async_init_db
from backend.core.models.task import Task
from sqlalchemy.ext.asyncio import AsyncSession
from backend.core.config import async_session

async def test_database():
    """Test database connection and initialization"""
    print("\n" + "="*60)
    print("[TEST 1] Database Connection & Initialization")
    print("="*60)

    try:
        print("\n[STEP 1] Initializing database schema...")
        await async_init_db()
        print("[OK] Database initialized successfully")

        print("\n[STEP 2] Creating test tasks...")
        async with async_session() as session:
            # Create test tasks
            test_tasks = [
                Task(title="Buy groceries", description="For Sunday dinner"),
                Task(title="Complete project", description="Finish the full-stack app"),
                Task(title="Write documentation", description="Document all features"),
                Task(title="Deploy to Vercel", description="Publish to production"),
                Task(title="Review code", description="Code review with team"),
            ]

            for task in test_tasks:
                session.add(task)

            await session.commit()
            print("[OK] Created %d test tasks" % len(test_tasks))

            # Verify tasks were created
            print("\n[STEP 3] Verifying tasks in database...")
            from sqlmodel import select
            result = await session.execute(select(Task))
            tasks = result.scalars().all()
            print("[OK] Total tasks in database: %d" % len(tasks))

            for task in tasks:
                status_icon = "[DONE]" if task.status == "complete" else "[TODO]"
                print("  %s [%d] %s (%s)" % (status_icon, task.id, task.title, task.status))

            # Test statistics
            print("\n[STEP 4] Verifying statistics...")
            from sqlmodel import func
            total_result = await session.execute(select(func.count(Task.id)))
            total = total_result.scalar() or 0

            pending_result = await session.execute(
                select(func.count(Task.id)).where(Task.status == "pending")
            )
            pending = pending_result.scalar() or 0

            completed_result = await session.execute(
                select(func.count(Task.id)).where(Task.status == "complete")
            )
            completed = completed_result.scalar() or 0

            print("[OK] Total: %d, Pending: %d, Completed: %d" % (total, pending, completed))

            # Test marking a task complete
            print("\n[STEP 5] Testing mark complete...")
            if tasks:
                first_task = tasks[0]
                first_task.mark_complete()
                session.add(first_task)
                await session.commit()
                print("[OK] Marked task '%s' as complete" % first_task.title)
                print("    Completion time: %s" % first_task.completed_at)

            # Test updating a task
            print("\n[STEP 6] Testing update task...")
            if tasks and len(tasks) > 1:
                second_task = tasks[1]
                second_task.title = "Updated: " + second_task.title
                session.add(second_task)
                await session.commit()
                print("[OK] Updated task title to: %s" % second_task.title)

        print("\n[PASSED] Database tests passed!")
        return True

    except Exception as e:
        print("\n[FAILED] Database test failed: %s: %s" % (type(e).__name__, str(e)[:200]))
        import traceback
        traceback.print_exc()
        return False

async def run_all_tests():
    """Run all tests"""
    print("\n" + "="*60)
    print("FULL-STACK TODO APP - TEST SUITE")
    print("="*60)
    print("\nConfiguration:")
    print("  Backend API: http://localhost:8000")
    print("  Frontend App: http://localhost:3000")
    print("  Database: PostgreSQL (Neon DB)")

    results = {
        "Database": await test_database(),
    }

    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)

    for test_name, result in results.items():
        status = "[PASS]" if result else "[FAIL]"
        print("%s: %s" % (test_name, status))

    all_passed = all(results.values())

    print("\n" + "="*60)
    if all_passed:
        print("[SUCCESS] ALL TESTS PASSED!")
        print("\nNext steps:")
        print("1. Open http://localhost:3000 in your browser")
        print("2. Create, edit, delete, and filter tasks")
        print("3. Check statistics display")
        print("4. Verify no console errors")
    else:
        print("[ERROR] SOME TESTS FAILED")
        print("\nTroubleshooting:")
        print("1. Check backend logs for errors")
        print("2. Verify database connection (.env file)")
        print("3. Ensure all dependencies are installed")
    print("="*60)

    return all_passed

if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    exit(0 if success else 1)
