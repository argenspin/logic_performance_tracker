from odoo import models,api,fields
import logging
import random
class LogicEmployeePerformance(models.Model):
    _name = "logic.employee.performance"
    @api.model
    def model_records_open_action(self,employee_id,model_name,start_date=False,end_date=False):
        domain=[]
        logger = logging.getLogger("Debugger: ")

        employee = self.env['hr.employee'].browse(int(employee_id))
        if model_name=="upaya.form":
            domain = [['coordinator_id','=',employee.user_id.id]]
        elif model_name=="yes_plus.logic":
            domain = [['coordinator_id','=',employee.user_id.id]]
        elif model_name=="student.faculty":
            domain = [['coordinator','=',employee.user_id.id]]
        elif model_name=="exam.details":
            domain = [['coordinator','=',employee.user_id.id]]
        elif model_name=="one_to_one.meeting":
            domain = [['coordinator_id','=',employee.user_id.id]]
        elif model_name=="logic.mock_interview":
            domain = [['coordinator','=',employee.user_id.id]]
        elif model_name=="logic.cip.form":
            domain = [['coordinator_id','=',employee.user_id.id]]
        elif model_name=="bring.your.buddy":
            domain = [['coordinator_id','=',employee.user_id.id]]
        logger.error("domain: "+str(domain))
        return domain
    
    def get_monthly_misc_counts(self,employee,year):
        misc_tasks = self.env['logic.task.other'].sudo().search([('task_creator_employee','=',employee.id),('state','=','completed')])
        misc_tasks = misc_tasks.filtered(lambda task: (task.date_completed or task.date).year==year)
        misc_data = {1:0, 2:0, 3:0, 4:0, 5:0, 6:0, 7:0, 8:0, 9:0, 10:0, 11:0, 12:0}
        for task in misc_tasks:
            if task.date_completed or task.date:
                date = task.date_completed or task.date
                misc_data[date.month]+=1
        return list(misc_data.values())

    def get_monthly_to_do_counts(self,employee,year):
        to_do_tasks = self.env['to_do.tasks'].sudo().search([('state','=','completed'),'|',('assigned_to','=',employee.user_id.id),('coworkers_ids','in',[employee.user_id.id] )])
        to_do_tasks = to_do_tasks.filtered(lambda task: task.assigned_date.year==year)
        to_do_data = {1:0, 2:0, 3:0, 4:0, 5:0, 6:0, 7:0, 8:0, 9:0, 10:0, 11:0, 12:0}
        for task in to_do_tasks:
            if task.assigned_date:
                date = task.assigned_date
                to_do_data[date.month]+=1
        return list(to_do_data.values())
    
    def get_monthly_digital_counts(self,employee,year):
        digital_tasks = self.env['digital.task'].sudo().search([('state','=','completed'),('assigned_execs','in',[employee.user_id.id] )])
        digital_tasks = digital_tasks.filtered(lambda task: task.date_completed.year==year)
        digital_data = {1:0, 2:0, 3:0, 4:0, 5:0, 6:0, 7:0, 8:0, 9:0, 10:0, 11:0, 12:0}
        for task in digital_tasks:
            if task.date_completed:
                date = task.date_completed
                digital_data[date.month]+=1
        return list(digital_data.values())

    @api.model
    def get_line_chart_datasets(self,employee_id,year="2023"):
        employee = self.env['hr.employee'].sudo().browse(int(employee_id))
        logger = logging.getLogger("Debugger: ")
        year = int(year)
        datasets = []
        logger.error(self.get_monthly_misc_counts(employee,year))
        misc_data = {
            'label': 'Miscellaneous Tasks',
            'backgroundColor': 'rgba(255,255,255, 0.2)',
            'borderColor': 'rgba(255, 0, 0, 0.6)',
            'borderWidth': 1,
            'data': self.get_monthly_misc_counts(employee,year)
        }
        to_do_data = {
            'label': 'To Do Tasks',
            'backgroundColor': 'rgba(255,255,255, 0.2)',
            'borderColor': 'rgba(25, 131, 19, 0.8)',
            'borderWidth': 1,
            'data': self.get_monthly_to_do_counts(employee,year)
        }
        datasets.append(misc_data)
        datasets.append(to_do_data)

        if employee.department_id.name=="Digital":
            digital_data = {
                'label': 'Digital Tasks',
                'backgroundColor': 'rgba(255,255,255, 0.2)',
                'borderColor': 'rgba(112, 63, 205, 0.8)',
                'borderWidth': 1,
                'data': self.get_monthly_digital_counts(employee,year)
            }
            datasets.append(digital_data)
        return datasets

    def get_employee_personal_data(self,employee):
        personal_data = {}
        personal_data['name'] = employee.name
        personal_data['job_title'] = employee.job_title
        personal_data['department_name'] = employee.department_id.name
        personal_data['image'] = 'data:image/png;base64, ' + str(employee.image_1920, 'UTF-8')
        return personal_data
    
    def get_student_feedback_average(self,employee):
        student_feedbacks = self.env['student.feedback'].sudo().search([('coordinator_id','=',employee.user_id.id)])
        if student_feedbacks:
            total_rating = 0
            for feedback in student_feedbacks:
                total_rating+= int(feedback.star_rating)
            average_rating = round(total_rating/len(student_feedbacks),2)
            return average_rating
        else:
            return 0
        
    def get_employee_academic_data(self,employee):
        academic_coord_perfs = self.env['academic.coordinator.performance'].sudo().search([('employee','=',employee.id)])
        if academic_coord_perfs:
            for coord_perf in academic_coord_perfs:
                academic_data = {}
                academic_data['name'] = coord_perf.employee.name
                academic_data['upaya_count'] = coord_perf.upaya_count
                academic_data['yes_plus_count'] = coord_perf.yes_plus_count
                academic_data['one2one_count'] = coord_perf.one2one_count
                academic_data['sfc_count'] = coord_perf.sfc_count
                academic_data['exam_count'] = coord_perf.exam_count
                academic_data['mock_interview_count'] = coord_perf.mock_interview_count
                academic_data['cip_excel_count'] = coord_perf.cip_excel_count
                academic_data['bring_buddy_count'] = coord_perf.bring_buddy_count
                academic_data['total_completed'] = coord_perf.total_completed
            
            academic_data['student_feedback_rating'] = self.get_student_feedback_average(employee)
            return academic_data
        else:
            return False
        
    def get_employee_marketing_data(self,employee,start_date=False,end_date=False):
        marketing_dept_obj = self.env['hr.department'].search([('name','=','Marketing')])
        if employee.department_id.id in marketing_dept_obj.child_ids.ids:
            rgba_colors = ['rgba(178, 56, 154, 0.75)', 'rgba(57, 141, 244, 0.52)', 'rgba(61, 14, 226, 0.88)', 'rgba(154, 29, 178, 0.51)', 'rgba(126, 101, 181, 0.05)', 'rgba(21, 80, 20, 0.70)', 'rgba(130, 79, 252, 0.09)', 'rgba(161, 125, 151, 0.61)', 'rgba(126, 124, 212, 0.81)', 'rgba(158, 94, 192, 0.75)', 'rgba(5, 19, 109, 0.87)', 'rgba(91, 247, 56, 0.89)', 'rgba(158, 182, 64, 0.12)', 'rgba(188, 190, 44, 0.53)', 'rgba(127, 164, 35, 0.92)', 'rgba(166, 173, 138, 0.32)', 'rgba(183, 241, 33, 0.89)', 'rgba(228, 183, 46, 0.94)', 'rgba(141, 226, 67, 0.39)', 'rgba(134, 126, 5, 0.13)', 'rgba(32, 190, 250, 0.85)', 'rgba(161, 59, 186, 0.20)', 'rgba(44, 217, 96, 0.68)', 'rgba(214, 67, 23, 0.77)', 'rgba(182, 127, 43, 0.94)', 'rgba(189, 3, 175, 0.71)', 'rgba(169, 148, 168, 0.69)', 'rgba(207, 205, 71, 0.74)', 'rgba(51, 140, 78, 0.42)', 'rgba(5, 246, 98, 0.81)', 'rgba(86, 128, 43, 0.90)', 'rgba(175, 77, 156, 0.63)', 'rgba(171, 104, 178, 0.31)', 'rgba(217, 229, 63, 0.47)', 'rgba(153, 138, 39, 0.09)', 'rgba(48, 141, 171, 0.01)', 'rgba(112, 207, 164, 0.50)', 'rgba(179, 184, 214, 0.61)', 'rgba(241, 14, 96, 0.44)', 'rgba(227, 53, 23, 0.54)', 'rgba(218, 215, 218, 0.87)', 'rgba(171, 194, 173, 0.57)', 'rgba(195, 154, 186, 0.04)', 'rgba(127, 118, 87, 0.01)', 'rgba(52, 222, 91, 0.32)', 'rgba(140, 238, 113, 0.55)', 'rgba(182, 249, 246, 0.76)', 'rgba(148, 12, 56, 0.61)', 'rgba(239, 154, 91, 0.33)', 'rgba(69, 251, 118, 0.25)']
            districts = dict(self.env['seminar.leads'].fields_get()['district']['selection'])
            district_names = list(dict(self.env['seminar.leads'].fields_get()['district']['selection']).values())
            employee_leads_data = {'districts':district_names, 'leads_dataset': [] }
            lead_counts = []
            leads_data = {
                'label': employee.name,
                'backgroundColor': rgba_colors.pop(random.randint(0,20)),
                'borderColor': 'rgba(27, 92, 196, 0.95)',
                'borderWidth': 1,
                'data': [0 for i in range(len(district_names))]
            }            
            for district in districts.keys():
                district_lead_count = self.env['marketing.tracker'].retrieve_employee_district_wise_lead_count(district,employee)
                lead_counts.append(district_lead_count)
            leads_data['data'] = lead_counts
            employee_leads_data['leads_dataset'].append(leads_data)
            return employee_leads_data
        else:
            return False

    def get_common_performance_data(self,employee):
        common_performance = {}
        common_performance['qualitative_rating'] = 0
        qualitative_perf = self.env['employee.qualitative.performance'].sudo().search([('employee','=',employee.id)])
        if qualitative_perf:
            common_performance['qualitative_rating'] = qualitative_perf[0].overall_average
        common_performance['misc_task_count'] = self.env['logic.task.other'].sudo().search_count([('task_creator','=',employee.user_id.id),('state','=','completed')])
        common_performance['to_do_count'] = self.env['to_do.tasks'].sudo().search_count([('state','=','completed'),'|',('assigned_to','=',employee.user_id.id),('coworkers_ids','in',[employee.user_id.id] ), ('state','=','completed')])        
        return common_performance

    @api.model
    def retrieve_employee_performance(self,employee_id):
        logger = logging.getLogger("Debugger: ")
        employee = self.env['hr.employee'].sudo().browse(int(employee_id))
        employee_data = {}
        employee_data['years'] = [2023, 2024, 2025, 2026, 2027, 2028, 2029, 2030, 2031, 2032, 2033, 2034, 2035, 2036, 2037]

        employee_data['personal_data'] = self.get_employee_personal_data(employee)
        employee_data['academic_data'] = self.get_employee_academic_data(employee)
        employee_data['common_performance'] = self.get_common_performance_data(employee)
        employee_data['line_chart_datasets'] = self.get_line_chart_datasets(employee)
        employee_data['leads_data'] = self.get_employee_marketing_data(employee)
        return employee_data
