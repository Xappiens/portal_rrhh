# Portal RRHH - Documentación de Doctypes

## 📋 Campos de Doctypes

### 👤 Employee (Empleado)

#### Campos Estándar Principales
- `name` - ID único del empleado
- `employee_name` - Nombre completo del empleado
- `first_name` - Nombre
- `last_name` - Apellidos
- `company` - Empresa
- `department` - Departamento
- `designation` - Puesto/Designación
- `reports_to` - Jefe directo
- `status` - Estado (Active, Inactive, Suspended, Left)
- `date_of_joining` - Fecha de incorporación
- `employee_number` - Número de empleado
- `cell_number` - Teléfono móvil
- `personal_email` - Email personal
- `company_email` - Email corporativo

#### Campos Custom Principales
- `custom_dninie` - DNI/NIE
- `custom_no_seguridad_social` - Número de seguridad social
- `custom_nacionalidad` - Nacionalidad
- `custom_irpf` - IRPF
- `custom_discapacitado` - Discapacitado (Check)
- `custom_centro` - Centro
- `custom_hijos` - Hijos

### 📄 Job Offer (Oferta de Trabajo)

#### Campos Estándar Principales
- `name` - ID único de la oferta
- `job_applicant` - Solicitante de trabajo
- `applicant_name` - Nombre del solicitante
- `applicant_email` - Email del solicitante
- `status` - Estado (Awaiting Response, Accepted, Rejected)
- `offer_date` - Fecha de la oferta
- `designation` - Designación/Puesto
- `company` - Empresa

#### Campos Custom Principales
- `custom_dninie` - DNI/NIE
- `custom_fecha_inicio` - Fecha de inicio
- `custom_fecha_fin` - Fecha de fin
- `custom_tipo_de_contrato` - Tipo de contrato
- `custom_estado_de_tramitacion` - Estado de tramitación
- `custom_firmado` - Firmado (Check)
- `custom_contrato` - Contrato (Check)
- `custom_comun` - Común (Check)
- `workflow_state` - Estado del workflow
- `curso` - Curso
- `expediente` - Expediente
- `centro_formacion` - Centro de formación

### 📝 Modificaciones RRHH

#### Campos Estándar Principales
- `name` - ID único de la modificación
- `company` - Empresa
- `employee` - Empleado
- `designation` - Puesto/Designación
- `start_date` - Fecha de inicio
- `end_date` - Fecha de fin
- `status` - Estado (Esperando Respuesta, Accepted, Rejected)
- `job_offer` - Hoja de contratación
- `tipo_actualizacion` - Tipo de actualización

#### Campos Custom Principales
- `custom_estado_de_tramitacion` - Estado de la tramitación
- `custom_tipo_de_contrato` - Tipo de contrato
- `custom_provincia` - Provincia
- `custom_firmado` - Firmado (Check)
- `custom_comun` - Común (Check)
- `workflow_state` - Estado del workflow

## 🔗 Relaciones entre Doctypes

### Employee ↔ Job Offer
- `Employee.job_applicant` → `Job Offer.job_applicant`
- `Job Offer.applicant_name` ← `Employee.employee_name`

### Job Offer ↔ Modificaciones RRHH
- `Modificaciones RRHH.job_offer` → `Job Offer.name`
- `Modificaciones RRHH.employee` → `Employee.name`

## 📊 Campos Clave para Portal RRHH

### Para Lista de Empleados
- `employee_name` - Nombre completo
- `company` - Empresa
- `designation` - Puesto
- `reports_to` - Responsable
- `date_of_joining` - Fecha de alta
- `status` - Estado
- `custom_dninie` - DNI/NIE

### Para Job Offers
- `applicant_name` - Nombre del empleado
- `status` - Estado (Awaiting Response, Accepted, Rejected)
- `custom_fecha_inicio` - Fecha de inicio
- `custom_fecha_fin` - Fecha de fin
- `designation` - Puesto
- `company` - Empresa
- `custom_tipo_de_contrato` - Tipo de contrato
- `custom_estado_de_tramitacion` - Estado de tramitación
# portal_rrhh
