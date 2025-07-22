import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { FormBuilder, FormGroup, FormsModule, ReactiveFormsModule, Validators } from '@angular/forms';
import { AuthService } from 'src/app/core/services/auth.service';
import { TaskOut, TaskComment } from 'src/app/core/interfaces/task.interface';

@Component({
  selector: 'app-employee-task',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, FormsModule],
  templateUrl: './employee-task.component.html',
  styleUrls: ['./employee-task.component.css']
})
export class EmployeeTaskComponent implements OnInit {
  tasks: TaskOut[] = [];
  filteredTasks: TaskOut[] = []; // Will hold all tasks initially
  isModalOpen = false;
  selectedTaskId: string | null = null;
  commentForm: FormGroup;
  errorMessage: string | null = null;
  filterDate: string = ''; // Empty string to disable date filter initially
  searchQuery: string = '';

  constructor(
    private http: HttpClient,
    private authService: AuthService,
    private fb: FormBuilder
  ) {
    this.commentForm = this.fb.group({
      user_id: ['', [Validators.required]],
      message: ['', [Validators.required]]
    });
  }

  ngOnInit() {
    this.loadMyTasks();
  }

  loadMyTasks() {
    const token = this.authService.getToken();
    if (!token) {
      console.error('No token available. Please log in.');
      return;
    }
    const headers = new HttpHeaders().set('Authorization', `Bearer ${token}`);

    this.http.get<TaskOut[]>(`http://localhost:8000/tasks/my`, { headers }).subscribe({
      next: (data) => {
        this.tasks = data;
        this.filteredTasks = [...this.tasks]; // Copy all tasks initially
        console.log('Loaded My Tasks:', data);
      },
      error: (err) => console.error('Error loading my tasks:', err)
    });
  }

  applyFilters() {
    this.filteredTasks = this.tasks.filter(task => {
      let taskDate: string | null = null;
      if (task.created_at) {
        try {
          const dateObj = new Date(task.created_at);
          if (!isNaN(dateObj.getTime())) {
            taskDate = dateObj.toISOString().split('T')[0];
          } else {
            console.warn(`Invalid date for task ${task.id}: ${task.due_date}`);
          }
        } catch (error) {
          console.warn(`Error parsing date for task ${task.id}: ${error}`);
        }
      }

      const matchesDate = !this.filterDate || (taskDate && taskDate === this.filterDate);
      const matchesSearch = !this.searchQuery || (task.title && task.title.toLowerCase().includes(this.searchQuery.toLowerCase()));
      return matchesDate && matchesSearch;
    });
  }

  updateTaskStatus(taskId: string, event: Event) {
    const selectElement = event.target as HTMLSelectElement;
    const newStatus = selectElement.value;
    if (newStatus) {
      const token = this.authService.getToken();
      if (!token) {
        console.error('No token available. Please log in.');
        return;
      }
      const headers = new HttpHeaders().set('Authorization', `Bearer ${token}`);

      this.http.patch<TaskOut>(`http://localhost:8000/tasks/${taskId}/status`, { status: newStatus }, { headers }).subscribe({
        next: (response) => {
          console.log('Task status updated:', response);
          this.loadMyTasks();
        },
        error: (err) => {
          console.error('Error updating task status:', err);
          this.errorMessage = err.error.detail || 'Error updating task status';
        }
      });
    }
  }

  openCommentModal(taskId: string) {
    this.selectedTaskId = taskId;
    this.isModalOpen = true;
    this.commentForm.reset();
    this.errorMessage = null;
  }

  closeCommentModal() {
    this.isModalOpen = false;
    this.selectedTaskId = null;
    this.errorMessage = null;
  }

  onSubmitComment() {
    if (this.commentForm.valid && this.selectedTaskId) {
      const commentData: TaskComment = this.commentForm.value;
      const token = this.authService.getToken();
      if (!token) {
        console.error('No token available. Please log in.');
        return;
      }
      const headers = new HttpHeaders().set('Authorization', `Bearer ${token}`);

      this.http.post<TaskOut>(`http://localhost:8000/tasks/${this.selectedTaskId}/comment`, commentData, { headers }).subscribe({
        next: (response) => {
          console.log('Comment added:', response);
          this.closeCommentModal();
          this.loadMyTasks();
        },
        error: (err) => {
          console.error('Error adding comment:', err);
          this.errorMessage = err.error.detail || 'Error adding comment';
        }
      });
    }
  }

  onDateChange(event: Event) {
    const target = event.target as HTMLInputElement;
    this.filterDate = target.value || '';
    this.applyFilters();
  }

  onSearchChange(event: Event) {
    const target = event.target as HTMLInputElement;
    this.searchQuery = target.value || '';
    this.applyFilters();
  }
}