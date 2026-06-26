from memory.db_manager import DatabaseManager
from datetime import datetime, timedelta

class MissionSystem:
    """Manages the JARVIS AI Mission and Goal system."""
    
    def __init__(self, db_manager: DatabaseManager = None):
        self.db = db_manager or DatabaseManager()

    def create_mission(self, name: str, deadline_days: int = 7) -> str:
        """Initializes a new mission project with a target deadline."""
        name = name.strip()
        deadline = (datetime.now() + timedelta(days=deadline_days)).strftime("%Y-%m-%d")
        
        # Create a default tracking task for the mission itself
        self.db.add_task(
            task_desc=f"Launch and organize details for mission: {name}",
            mission_name=name,
            deadline=deadline
        )
        return f"Mission '{name}' has been successfully created. The target deadline is set to {deadline}."

    def add_mission_task(self, name: str, task_desc: str) -> str:
        """Appends a checklist task under an active mission."""
        name = name.strip()
        # Find if mission exists by looking up any task under it
        existing = self.db.get_tasks(mission_name=name)
        if not existing:
            # Auto-create mission with default 7 days deadline
            self.create_mission(name)
            
        deadline = existing[0]["deadline"] if existing else (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
        self.db.add_task(task_desc=task_desc, mission_name=name, deadline=deadline)
        return f"Appended task: '{task_desc}' under mission '{name}'."

    def complete_mission_task(self, task_id: int) -> str:
        """Marks a task as completed and recalculates overall mission progress."""
        # Find the task
        tasks = self.db.get_tasks()
        target_task = None
        for t in tasks:
            if t["id"] == task_id:
                target_task = t
                break
                
        if not target_task:
            return f"Task ID {task_id} not found."
            
        mission_name = target_task["mission_name"]
        self.db.update_task_status(task_id, "completed", progress=100)
        
        # If part of a mission, update all other tasks' overall progress indicator
        if mission_name:
            m_tasks = self.db.get_tasks(mission_name=mission_name)
            completed_count = sum(1 for t in m_tasks if t["status"] == "completed")
            total_count = len(m_tasks)
            new_progress = int((completed_count / total_count) * 100)
            
            # Update all tasks under this mission with the updated progress metric
            for t in m_tasks:
                self.db.update_task_status(t["id"], t["status"], progress=new_progress)
                
            return f"Task marked completed. Mission '{mission_name}' is now at {new_progress}% progress."
            
        return "Task marked completed."

    def get_mission_report(self, name: str) -> str:
        """Generates a detailed summary of a mission, list of tasks, deadlines and status."""
        name = name.strip()
        tasks = self.db.get_tasks(mission_name=name)
        
        if not tasks:
            return f"No records found for mission '{name}'."
            
        progress = tasks[0]["progress"]
        deadline = tasks[0]["deadline"]
        
        report = f"📋 JARVIS Mission Status Report: '{name}'\n"
        report += f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        report += f"📅 Deadline: {deadline} | 📊 Overall Progress: {progress}%\n\n"
        report += "Checklist Details:\n"
        
        for t in tasks:
            status_icon = "✅" if t["status"] == "completed" else "⬜"
            report += f"  {status_icon} [ID: {t['id']}] {t['task_desc']}\n"
            
        return report

    def get_all_active_missions(self) -> dict:
        """Returns a dict of all active missions and their overall progress."""
        tasks = self.db.get_tasks()
        missions = {}
        for t in tasks:
            m_name = t["mission_name"]
            if m_name:
                if m_name not in missions:
                    missions[m_name] = {
                        "progress": t["progress"],
                        "deadline": t["deadline"],
                        "pending_count": 0,
                        "total_count": 0
                    }
                missions[m_name]["total_count"] += 1
                if t["status"] == "pending":
                    missions[m_name]["pending_count"] += 1
                    
        return missions
