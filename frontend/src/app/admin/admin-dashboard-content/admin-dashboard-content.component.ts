import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { AuthService } from 'src/app/core/services/auth.service';
import { LeaveResponse } from 'src/app/core/interfaces/leave.interface';
import { FormsModule } from '@angular/forms';
import Chart from 'chart.js/auto';

@Component({
  selector: 'app-admin-dashboard-content',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './admin-dashboard-content.component.html',
  styleUrls: ['./admin-dashboard-content.component.css']
})
export class AdminDashboardContentComponent implements OnInit {
  pendingLeaves: LeaveResponse[] = [];
  adminName: string | null = null;
  thoughtForTheDay: string = '';
  todoList: string[] = [];
  newTodo: string = '';
  employees: any[] = [];
  private chartInstance: Chart | null = null;

  constructor(private http: HttpClient, private authService: AuthService) {}

  ngOnInit() {
    this.loadPendingLeaveRequests();
    this.adminName = this.authService.getAdminName();
    this.generateThoughtForTheDay();
    this.loadTodoList();
    this.loadEmployees();
    this.renderChart();
  }
  
  loadPendingLeaveRequests() {
    const token = this.authService.getToken();
    if (!token) {
      console.error('No token available. Please log in.');
      return;
    }
    const headers = new HttpHeaders().set('Authorization', `Bearer ${token}`);

    this.http.get<LeaveResponse[]>(`http://localhost:8000/admin/leave/pendingrequests`, { headers }).subscribe({
      next: (data) => {
        this.pendingLeaves = data;
      },
      error: (err) => console.error('Error loading pending leave requests:', err)
    });
  }

  get pendingLeavesCount(): number {
    return this.pendingLeaves.length;
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

  loadEmployees() {
    const token = this.authService.getToken();
    if (!token) {
      console.error('No token available. Please log in as an admin.');
      return;
    }
    const headers = new HttpHeaders().set('Authorization', `Bearer ${token}`);

    // Try a different endpoint based on your backend
    this.http.get<any[]>('http://localhost:8000/employee/getall', { headers }) // Removed /api/ prefix
      .subscribe({
        next: (data) => {
          this.employees = data;
          console.log('Loaded Employees:', data); // Debug: Check the data structure
          this.renderChart();
        },
        error: (err) => {
          console.error('Error loading employees:', err);
          // Fallback to mock data if API fails
          // this.employees = [
          //   { department: 'HR', emp_code: 'E001' },
          //   { department: 'IT', emp_code: 'E002' },
          //   { department: 'HR', emp_code: 'E003' },
          //   { department: 'IT', emp_code: 'E004' },
          //   { department: 'Finance', emp_code: 'E005' }
          // ];
          // this.renderChart();
        }
      });
  }

  getEmployeesByDepartment(): { department: string, count: number }[] {
    const counts: { [key: string]: number } = {};
    this.employees.forEach(employee => {
      const dept = employee.department || 'Unknown';
      counts[dept] = (counts[dept] || 0) + 1;
    });
    return Object.entries(counts).map(([department, count]) => ({ department, count }));
  }

  renderChart() {
    if (this.chartInstance) {
      this.chartInstance.destroy(); // Destroy previous chart instance
    }

    const departments = this.getEmployeesByDepartment();
    const ctx = (document.getElementById('departmentChart') as HTMLCanvasElement).getContext('2d');
    if (ctx && departments.length > 0) {
      this.chartInstance = new Chart(ctx, {
        type: 'bar',
        data: {
          labels: departments.map(d => d.department), // Departments on y-axis
          datasets: [{
            label: 'Employees',
            data: departments.map(d => d.count), // Multiply by 10 to simulate 10-100 range
            backgroundColor: ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF', '#FF9F40']
          }]
        },
        options: {
          indexAxis: 'y', // Swap axes to put departments on y-axis
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            x: {
              beginAtZero: true, // Start x-axis at 0
              title: {
                display: true,
                text: 'Count'
              },
              ticks: {
                stepSize: 1, // Integer steps
                precision: 0 // No decimals
              },
              min: 0, // Minimum value
              max: 10 // Maximum value to match your 10-100 range
            },
            y: {
              title: {
                display: true,
                text: 'Department'
              }
            }
          },
          plugins: {
            legend: {
              display: true
            }
          }
        }
      });
    } else {
      console.warn('No departments data available to render chart.');
    }
  }
}