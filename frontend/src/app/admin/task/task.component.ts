import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { TaskCreate, TaskOut, TaskUpdate } from 'src/app/core/interfaces/task.interface';
import { TaskService } from 'src/app/core/services/task.service';
import { AuthService } from 'src/app/core/services/auth.service';
import { EmployeeService } from 'src/app/core/services/employee.service';
import { EmployeeOut } from 'src/app/core/interfaces/employee.interface';

@Component({
  selector: 'app-tasks',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
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
  filterStatus: string | null = null;
  emp_names: EmployeeOut[] = []
  filteredNames: string[] = []
  showSuggestions = false

  constructor(
    private fb: FormBuilder,
    private taskService: TaskService,
    private authService: AuthService,
    private employeeService: EmployeeService
  ) {
    this.taskForm = this.fb.group({
      title: ['', [Validators.required]],
      description: ['', [Validators.required]],
      assigned_to: [''],
      assigned_by: ['', [Validators.required]],
      priority: ['Normal', [Validators.required]],
      due_date: [''],
      status: ['', [Validators.required]],
      project: ['', [Validators.required]]
    });
  }

  ngOnInit() {
    this.loadTasks();
    this.loadEmployees();
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
          assigned_to: task.assigned_to.length ? task.assigned_to.join(', ') : '',
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
      const formValue = this.taskForm.value;
     
      const assignedToEmails = typeof formValue.assigned_to === 'string' && formValue.assigned_to.trim()
        ? formValue.assigned_to.split(',').map((email: string) => email.trim())
        : [];

     
      const taskData = {
        title: formValue.title,
        description: formValue.description,
        assigned_to: assignedToEmails,
        assigned_by: formValue.assigned_by,
        priority: formValue.priority,
        due_date: formValue.due_date || '',
        status: formValue.status,
        project: formValue.project
      };

      console.log('Submitting Data:', taskData);

      if (this.selectedTaskId) {
       
        const updateData: TaskUpdate = taskData;
        this.taskService.updateTask(this.selectedTaskId, updateData).subscribe({
          next: (response) => {
            console.log('Task updated:', response);
            this.closeModal();
            this.loadTasks();
          },
          error: (err) => {
            console.error('Error updating task:', err.message);
            this.errorMessage = `Error updating task: ${err.message || 'Unknown error'}`;
          }
        });
      } else {
      
        const createData: TaskCreate = taskData;
        this.taskService.createTask(createData).subscribe({
          next: (response) => {
            console.log('Task added:', response);
            this.closeModal();
            this.loadTasks();
          },
          error: (err) => {
            console.error('Error adding task:', err.message);
            this.errorMessage = `Error adding task: ${err.message || 'Unknown error'}`;
          }
        });
      }
    }
  }

  loadTasks() {
    this.taskService.getAllTasks().subscribe({
      next: (data) => {
        this.tasks = data;
        this.filterTasks();
        console.log('Loaded Tasks:', data);
      },
      error: (err) => {
        console.error('Error loading tasks:', err.message);
        this.errorMessage = `Error loading tasks: ${err.message || 'Unknown error'}`;
      }
    });
  }

  deleteTask(taskId: string) {
    if (!taskId) {
      console.error('taskId is undefined in deleteTask');
      this.errorMessage = 'Error deleting task: Task ID is undefined';
      return;
    }
    if(confirm('Are you sure you want to delete this leave request?')){
      this.taskService.deleteTask(taskId).subscribe({
        next: (response) => {
          console.log('Task deleted:', response);
          this.loadTasks();
        },
        error: (err) => {
          console.error('Error deleting task:', err.message);
          this.errorMessage = `Error deleting task: ${err.message || 'Unknown error'}`;
        }
      });
    }
  }

  filterTasks() {
    this.filteredTasks = this.tasks.filter(task => {
      const priority = task.priority || '';
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

      const matchesStatus = !this.filterStatus || task.status === this.filterStatus

      return matchesSearch && matchesDate && matchesStatus;

    });
  }

  loadEmployees() {
    this.employeeService.getAllEmployees().subscribe({
      next: (data) => {
        this.emp_names = data;
        console.log('Loaded Employees:', data);
      },
      error: (err) => {
        console.error('Error loading employees:', err.message);
        this.errorMessage = `Error loading employees: ${err.message || 'Unknown error'}`;
      }
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

  onFilterStatus(event: Event) {
    this.filterStatus = (event.target as HTMLInputElement).value;
    this.filterTasks();
  }


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