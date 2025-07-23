import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { AuthService } from 'src/app/core/services/auth.service';
import { HttpClient,HttpHeaders } from '@angular/common/http';
import { LeaveResponse } from 'src/app/core/interfaces/leave.interface';
import { Chart } from 'chart.js/auto';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-employee-dashboard-content',
  standalone: true,
  imports: [CommonModule,FormsModule],
  templateUrl: './employee-dashboard-content.component.html',
  styleUrls: ['./employee-dashboard-content.component.css']
})
export class EmployeeDashboardContentComponent {
    remainingLeaves: LeaveResponse[] = [];
    employeeName: string | null = null;
    thoughtForTheDay: string = '';
    todoList: string[] = [];
    newTodo: string = '';
    
  
    constructor(private http: HttpClient, private authService: AuthService) {}
  
    ngOnInit() {
      this.loadRemainingLeaveRequests();
      this.employeeName = this.authService.getUserName();
      this.generateThoughtForTheDay();
      this.loadTodoList();
    }
    
    loadRemainingLeaveRequests() {
      const token = this.authService.getToken();
      if (!token) {
        console.error('No token available. Please log in.');
        return;
      }
      const headers = new HttpHeaders().set('Authorization', `Bearer ${token}`);
  
      this.http.get<LeaveResponse[]>(`http://localhost:8000/Emp_leave/my-requests`, { headers }).subscribe({
        next: (data) => {
          console.log(data)
          this.remainingLeaves = data;
        },
        error: (err) => console.error('Error loading pending leave requests:', err)
      });
    }
  
  get totalLeavesTaken(): number {
    return this.remainingLeaves
      .filter(leave => leave.status === 'approved') // Only count approved leaves
      .reduce((sum, leave) => sum + leave.days, 0); // Sum the days of approved leaves
  }

  get remainingLeavesCount(): number {
    const initialLeaves = 20; // Assuming initial leave balance is 20 days
    return initialLeaves - this.totalLeavesTaken; // Remaining = Initial - Total Taken
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
  
}
