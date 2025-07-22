import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { HttpClient, HttpClientModule, HttpHeaders } from '@angular/common/http';
import { TaskCreate, TaskOut, TaskUpdate } from 'src/app/core/interfaces/task.interface';
import { AuthService } from 'src/app/core/services/auth.service';

@Component({
  selector: 'app-tasks',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, HttpClientModule],
  templateUrl: './task.component.html',
  styleUrls: ['./task.component.css']
})
export class TaskComponent implements OnInit {
  isModalOpen = false;
  taskForm: FormGroup;
  tasks: TaskOut[] = [];
  filteredTasks: TaskOut[] = [];
  ttlempicon: string = '';
  selectedTaskId: string | null = null;
  errorMessage: string | null = null;
  searchTerm: string = '';
  filterDate: string = '';

  constructor(private fb: FormBuilder, private http: HttpClient, private authService: AuthService) {
    this.taskForm = this.fb.group({
      title: ['', [Validators.required]],
      description: ['', [Validators.required]],
      assigned_to_emails: [''], 
      assigned_by: ['', [Validators.required]],
      priority: ['Normal'],
      due_date: [''],
      status: ['', [Validators.required]],
      project: ['', [Validators.required]]
    });
    
  }

  ngOnInit() {
    this.loadTasks();
  }

  openModal(taskId: string | null = null) {
    this.isModalOpen = true;
    this.selectedTaskId = taskId;
    this.taskForm.reset();
    this.errorMessage = null;

    if (taskId && this.tasks.length > 0) {
      const task = this.tasks.find(t => t.id === taskId);
      if (task) {
        console.log('Pre-filling with:', task);
        this.taskForm.patchValue({
          title: task.title || '',
          description: task.description || '',
          assigned_to_emails: task.assigned_to.length ? task.assigned_to.join(', ') : '', 
          assigned_by: task.assigned_by || '',
          priority: task.priority || 'Normal',
          due_date: task.due_date || '',
          status: task.status || '',
          project: task.project || ''
        });
      } else {
        console.warn('Task not found for id:', taskId);
      }
    }
  }

  closeModal() {
    this.isModalOpen = false;
    this.taskForm.reset();
    this.selectedTaskId = null;
    this.errorMessage = null;
  }

  onSubmit() {
    if (this.taskForm.valid) {
      let taskData: TaskCreate | TaskUpdate = { ...this.taskForm.value }; 
      if (typeof taskData.assigned_to_emails === 'string' && taskData.assigned_to_emails.trim()) {
        taskData.assigned_to_emails = taskData.assigned_to_emails.split(',').map((email: string) => email.trim());
      } else if (!Array.isArray(taskData.assigned_to_emails)) {
        taskData.assigned_to_emails = [];
      }
      console.log('Submitting Data:', taskData);
      const token = this.authService.getToken();
      if (!token) {
        console.error('No token available. Please log in.');
        return;
      }
      const headers = new HttpHeaders().set('Authorization', `Bearer ${token}`);

      if (this.selectedTaskId) {
        this.http.put(`http://localhost:8000/tasks/${this.selectedTaskId}`, taskData, { headers }).subscribe({
          next: (response) => {
            console.log('Task updated:', response);
            this.closeModal();
            this.loadTasks();
          },
          error: (err) => {
            console.error('Error updating task:', err);
            this.errorMessage = err.error.detail || 'Error updating task';
          }
        });
      } else {
        this.http.post('http://localhost:8000/tasks/', taskData, { headers }).subscribe({
          next: (response) => {
            console.log('Task added:', response);
            this.closeModal();
            this.loadTasks();
          },
          error: (err) => {
            console.error('Error adding task:', err);
            this.errorMessage = err.error.detail || 'Error adding task';
          }
        });
      }
    }
  }

  loadTasks() {
    const token = this.authService.getToken();
    if (!token) {
      console.error('No token available. Please log in as an admin.');
      return;
    }
    const headers = new HttpHeaders().set('Authorization', `Bearer ${token}`);

    this.http.get<TaskOut[]>('http://localhost:8000/tasks/', { headers }).subscribe({
      next: (data) => {
        this.tasks = data;
        this.filterTasks();
        console.log('Loaded Tasks:', data);
      },
      error: (err) => console.error('Error loading tasks:', err)
    });
  }

  deleteTask(taskId: string) {
    if (!taskId) {
      console.error('taskId is undefined in deleteTask');
      return;
    }
    const token = this.authService.getToken();
    if (!token) {
      console.error('No token available. Please log in as an admin.');
      return;
    }
    const headers = new HttpHeaders().set('Authorization', `Bearer ${token}`);

    this.http.delete(`http://localhost:8000/tasks/${taskId}`, { headers }).subscribe({
      next: (response) => {
        console.log('Task deleted:', response);
        this.loadTasks();
      },
      error: (err) => {
        console.error('Error deleting task:', err);
        this.errorMessage = err.error?.detail || 'Error deleting task';
      }
    });
  }

  filterTasks() {
    this.filteredTasks = this.tasks.filter(task => {
      const priority = task.priority || ''; // Default to empty string if undefined
      const dueDateStr = task.due_date ? task.due_date.toString() : '';
      const createdAtStr = task.created_at ? task.created_at.toString() : '';

      const matchesSearch = !this.searchTerm || 
        task.title.toLowerCase().includes(this.searchTerm.toLowerCase()) ||
        task.description.toLowerCase().includes(this.searchTerm.toLowerCase()) ||
        task.assigned_to.join(', ').toLowerCase().includes(this.searchTerm.toLowerCase()) ||
        task.assigned_by.toLowerCase().includes(this.searchTerm.toLowerCase()) ||
        task.status.toLowerCase().includes(this.searchTerm.toLowerCase()) ||
        priority.toLowerCase().includes(this.searchTerm.toLowerCase()) ||
        (task.project?.toLowerCase().includes(this.searchTerm.toLowerCase()) || false) ||
        dueDateStr.includes(this.searchTerm) ||
        createdAtStr.includes(this.searchTerm);

      const matchesDate = !this.filterDate || 
        createdAtStr.startsWith(this.filterDate);

      return matchesSearch && matchesDate;
    });
  }

  onSearch(event: Event) {
    this.searchTerm = (event.target as HTMLInputElement).value;
    this.filterTasks();
  }

  onDateFilter(event: Event) {
    this.filterDate = (event.target as HTMLInputElement).value;
    this.filterTasks();
  }

  // New methods to compute task counts
  getPendingTasksCount(): number {
    return this.tasks.filter(t => t.status === 'Pending').length;
  }

  getCompletedTasksCount(): number {
    return this.tasks.filter(t => t.status === 'Completed').length;
  }

  getOverdueTasksCount(): number {
    const now = new Date();
    return this.tasks.filter(t => t.due_date && new Date(t.due_date) < now).length;
  }
}