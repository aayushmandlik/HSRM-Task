export interface LeaveCreate {
  start_date: string;
  end_date: string;
  leave_type: string;
  reason: string;
}

export interface LeaveResponse {
  _id: string;
  employee_id: string;
  employee_name: string;
  start_date: string;
  end_date: string;
  leave_type: string;
  reason: string;
  status: string;
  days: number;
  created_at: string;
  updated_at: string;
  leave_taken: number;
  remaining_leaves: number;
  approved_by: string | null;
}