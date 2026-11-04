# Spec Delta: Core Configuration

## Purpose
Provee mecanismos centralizados y tipados para la carga, validación y acceso inmutable a los parámetros y credenciales del sistema desde variables de entorno y archivos de configuración.

## ADDED Requirements

### Requirement: Carga y validación estricta de variables de entorno
The system SHALL / El sistema DEBE cargar las variables de configuración en tiempo de arranque y validar estrictamente los tipos de datos requeridos, incluyendo la URL de conexión a la base de datos y los parámetros de pool.

#### Scenario: Carga exitosa con variables válidas
- **WHEN** la aplicación arranca con todas las variables requeridas definidas correctamente en el entorno o archivo de configuración
- **THEN** los valores quedan disponibles como atributos tipados e inmutables para el resto de la aplicación

#### Scenario: Fallo en arranque por configuración faltante o inválida
- **WHEN** la aplicación arranca sin la variable obligatoria de base de datos o con un formato de esquema inválido
- **THEN** el sistema interrumpe inmediatamente el booteo arrojando un error explícito de validación

### Requirement: Acceso singleton cacheado
The system SHALL / El sistema DEBE proveer un único punto de acceso cacheado a la configuración activa para prevenir lecturas redundantes del entorno durante el ciclo de vida del proceso.

#### Scenario: Múltiples solicitudes de configuración
- **WHEN** distintos componentes solicitan la instancia de configuración durante el procesamiento de peticiones
- **THEN** el sistema retorna la misma instancia en memoria sin reevaluar ni releer el entorno
