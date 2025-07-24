export interface CommentSchema {
  user_id: string;
  message: string;
  timestamp?: Date;
}

export interface TaskCreate {
  title: string;
  description: string;
  assigned_to_emails: string[];
  assigned_by: string;
  priority?: string;
  due_date?: Date;
  status: string;
  project: string;
}

export interface TaskUpdate {
  title?: string;
  description?: string;
  assigned_to_emails?: string[];
  assigned_by?: string;
  priority?: string;
  due_date?: Date;
  status?: string;
  project?: string;
}

export interface TaskComment {
  user_id: string;
  message: string;
}

export interface TaskOut {
  id: string;
  title: string;
  description: string;
  assigned_to: string[];
  assigned_by: string;
  status: string;
  priority?: string;
  due_date?: Date;
  created_at: Date;
  updated_at: Date;
  comments: CommentSchema[];
  project: string;
}