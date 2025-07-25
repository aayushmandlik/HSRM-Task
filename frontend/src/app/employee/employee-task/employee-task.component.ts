import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, FormsModule, ReactiveFormsModule, Validators } from '@angular/forms';
import { TaskOut, TaskComment } from 'src/app/core/interfaces/task.interface';
import { TaskService } from 'src/app/core/services/task.service';
import { AuthService } from 'src/app/core/services/auth.service';

@Component({
  selector: 'app-employee-task',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, FormsModule],
  templateUrl: './employee-task.component.html',
  styleUrls: ['./employee-task.component.css']
})
export class EmployeeTaskComponent implements OnInit {
  tasks: TaskOut[] = [];
  filteredTasks: TaskOut[] = [];
  isModalOpen = false;
  selectedTaskId: string | null = null;
  commentForm: FormGroup;
  errorMessage: string | null = null;
  filterDate: string = '';
  searchQuery: string = '';

  constructor(
    private taskService: TaskService,
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
    this.taskService.getMyTasks().subscribe({
      next: (data) => {
        this.tasks = data;
        this.filteredTasks = [...this.tasks];
        console.log('Loaded My Tasks:', data);
      },
      error: (err) => {
        console.error('Error loading my tasks:', err.message);
        this.errorMessage = `Error loading tasks: ${err.message || 'Unknown error'}`;
      }
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
            console.warn(`Invalid date for task ${task.id}: ${task.created_at}`);
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
      this.taskService.updateTaskStatus(taskId, newStatus).subscribe({
        next: (response) => {
          console.log('Task status updated:', response);
          this.loadMyTasks();
        },
        error: (err) => {
          console.error('Error updating task status:', err.message);
          this.errorMessage = `Error updating task status: ${err.message || 'Unknown error'}`;
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

  getPendingTasksCount(): number {
    return this.tasks.filter(t => t.status === 'Pending').length;
  }

  getCompletedTasksCount(): number {
    return this.tasks.filter(t => t.status === 'Completed').length;
  }

  getOverdueTasksCount(): number {
    const now = new Date();
    return this.tasks.filter(t => t.status!== 'Completed' && t.due_date && new Date(t.due_date) < now).length;
  }
}