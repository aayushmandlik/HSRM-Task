import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { AuthService } from 'src/app/core/services/auth.service';
import { HttpClient,HttpHeaders } from '@angular/common/http';
import { LeaveResponse } from 'src/app/core/interfaces/leave.interface';
import { Attendance } from 'src/app/core/interfaces/attendance.interface';
import { FormsModule } from '@angular/forms';
import { LeaveService } from 'src/app/core/services/leave.service';
import { AttendanceService } from 'src/app/core/services/attendance.service';
import { TaskOut } from 'src/app/core/interfaces/task.interface';
import { TaskService } from 'src/app/core/services/task.service';

@Component({
  selector: 'app-employee-dashboard-content',
  standalone: true,
  imports: [CommonModule,FormsModule],
  templateUrl: './employee-dashboard-content.component.html',
  styleUrls: ['./employee-dashboard-content.component.css']
})
export class EmployeeDashboardContentComponent {
    leaves: LeaveResponse[] = [];
    attendanceLogs: Attendance[] = []
    employeeName: string | null = null;
    errorMessage: string | null = null;
    thoughtForTheDay: string = '';
    todoList: string[] = [];
    newTodo: string = '';
    tasks: TaskOut[] = []
    
  
    constructor(private http: HttpClient, private authService: AuthService, private leaveService: LeaveService, private attendanceService: AttendanceService, private taskService: TaskService) {}
  
    ngOnInit() {
      this.loadMyLeaveRequests();
      this.loadAttendanceLogs();
      this.employeeName = this.authService.getUserName();
      this.generateThoughtForTheDay();
      this.loadTodoList();
      this.loadMyTasks();
    }
    
    loadMyLeaveRequests() {
      this.leaveService.getMyLeaveRequests().subscribe({
        next: (data) => {
          this.leaves = data;
          console.log('Loaded My Leave Requests:', data);
        },
        error: (err) => {
          console.error('Error loading my leave requests:', err.message);
          this.errorMessage = `Error loading my leave requests: ${err.message || 'Unknown error'}`;
        }
      });
    }

  
  loadAttendanceLogs() {
    this.attendanceService.getMyAttendanceLogs().subscribe({
      next: (data) => {
        this.attendanceLogs = data;
        console.log('Loaded My Attendance Logs:', this.attendanceLogs);
        this.errorMessage = null;
      },
      error: (err) => {
        console.error('Error loading my attendance logs:', err.message);
        this.errorMessage = `Error loading my attendance logs: ${err.message || 'Unknown error'}`;
      }
    });
  }

  loadMyTasks() {
    this.taskService.getMyTasks().subscribe({
      next: (data) => {
        this.tasks = data;
        console.log('Loaded My Tasks:', data);
      },
      error: (err) => {
        console.error('Error loading my tasks:', err.message);
        this.errorMessage = `Error loading tasks: ${err.message || 'Unknown error'}`;
      }
    });
  }
  
  get totalLeavesTaken(): number {
    return this.leaves
      .filter(leave => leave.status === 'approved') 
      .reduce((sum, leave) => sum + leave.days, 0); 
  }

  get remainingLeavesCount(): number {
    const initialLeaves = 20;
    return initialLeaves - this.totalLeavesTaken; 
  }
  
    generateThoughtForTheDay() {
      const thoughts = [
        "The best way to predict the future is to create it. - Peter Drucker",
        "Success is not final, failure is not fatal: It is the courage to continue that counts. - Winston Churchill",
        "Believe you can and you're halfway there. - Theodore Roosevelt",
        "The only way to do great work is to love what you do. - Steve Jobs",
        "Hardships often prepare ordinary people for an extraordinary destiny. - C.S. Lewis",
        "You are never too old to set another goal or to dream a new dream. - C.S. Lewis",
        "The secret of getting ahead is getting started. - Mark Twain",
        "It does not matter how slowly you go as long as you do not stop. - Confucius"
      ];
  
      const today = new Date();
      const dayIndex = today.getDate() % thoughts.length;
      this.thoughtForTheDay = thoughts[dayIndex];
    }
  
    loadTodoList() {
      const currentUser = this.authService.getCurrentUser();
      const userId = currentUser ? currentUser.user_id : 'default';
      const savedTodos = localStorage.getItem(`todos_${userId}`);
      this.todoList = savedTodos ? JSON.parse(savedTodos) : [];
    }
  
    addTodo() {
      if (this.newTodo.trim()) {
        this.todoList.push(this.newTodo.trim());
        this.newTodo = '';
        this.saveTodoList();
      }
    }
  
    deleteTodo(index: number) {
      this.todoList.splice(index, 1);
      this.saveTodoList();
    }
  
    saveTodoList() {
      const currentUser = this.authService.getCurrentUser();
      const userId = currentUser ? currentUser.user_id : 'default';
      localStorage.setItem(`todos_${userId}`, JSON.stringify(this.todoList));
    }

  getPendingTasksCount(): number {
    return this.tasks.filter(t => t.status === 'Pending').length;
  }

  getCompletedTasksCount(): number {
    return this.tasks.filter(t => t.status === 'Completed').length;
  }

  getInprogressTaskCount(): number{
    return this.tasks.filter(t => t.status === "InProgress").length;
  }
  
}
