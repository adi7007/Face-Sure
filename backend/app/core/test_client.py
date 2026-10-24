import httpx
import asyncio

async def test():
    async with httpx.AsyncClient(base_url="http://127.0.0.1:8000") as client:
        # 1. Create student
        payload = {
            "student_id": "STU-2026-004",
            "full_name": "David Miller",
            "department": "Computer Science",
            "academic_year": "2nd Year"
        }
        res = await client.post("/api/v1/students", json=payload)
        print("Create status:", res.status_code, res.json())

        # 2. List students
        res_list = await client.get("/api/v1/students")
        print("List students count:", len(res_list.json()))

if __name__ == "__main__":
    asyncio.run(test())
