export interface Attendance {
  id: string;
  user_id: string;
  check_in: string | null;
  check_out: string | null;
  break_in: string | null;
  break_out: string | null;
  status: 'Not Marked' | 'Present' | 'Absent';
  total_hours: number | null;
  employee_name: string | null;
}