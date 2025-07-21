export interface EmployeeCreate {
  user_id: string;
  emp_code: string;
  name: string;
  email: string;
  phone: string;
  gender?: string;
  dob?: string;
  address?: string;
  profile_image?: string;
  department: string;
  designation: string;
  date_of_joining: string;
  location: string;
  reporting_manager_id?: string;
  reporting_manager?: string;
  status?: string;
}

export interface EmployeeUpdate {
  name?: string;
  email?: string;
  phone?: string;
  gender?: string;
  dob?: string;
  address?: string;
  profile_image?: string;
  department?: string;
  designation?: string;
  date_of_joining?: string;
  location?: string;
  reporting_manager_id?: string;
  reporting_manager?: string;
  status?: string;
}

export interface EmployeeOut extends EmployeeCreate {
  _id: string;
  status: string;
}