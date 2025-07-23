export interface Attendance {
  id: string;
  user_id: string;
  check_in: string | null; // ISO datetime string
  check_out: string | null; // ISO datetime string
  break_in: string | null; // ISO datetime string
  break_out: string | null; // ISO datetime string
  status: 'Not Marked' | 'Present' | 'Absent';
  total_hours: number | null;
  employee_name: string | null;
}