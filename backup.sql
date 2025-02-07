PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS "django_migrations" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "app" varchar(255) NOT NULL, "name" varchar(255) NOT NULL, "applied" datetime NOT NULL);
INSERT INTO django_migrations VALUES(1,'contenttypes','0001_initial','2024-12-17 12:37:01.441165');
INSERT INTO django_migrations VALUES(2,'contenttypes','0002_remove_content_type_name','2024-12-17 12:37:01.446706');
INSERT INTO django_migrations VALUES(3,'auth','0001_initial','2024-12-17 12:37:01.446706');
INSERT INTO django_migrations VALUES(4,'auth','0002_alter_permission_name_max_length','2024-12-17 12:37:01.446706');
INSERT INTO django_migrations VALUES(5,'auth','0003_alter_user_email_max_length','2024-12-17 12:37:01.462337');
INSERT INTO django_migrations VALUES(6,'auth','0004_alter_user_username_opts','2024-12-17 12:37:01.462337');
INSERT INTO django_migrations VALUES(7,'auth','0005_alter_user_last_login_null','2024-12-17 12:37:01.462337');
INSERT INTO django_migrations VALUES(8,'auth','0006_require_contenttypes_0002','2024-12-17 12:37:01.477962');
INSERT INTO django_migrations VALUES(9,'auth','0007_alter_validators_add_error_messages','2024-12-17 12:37:01.477962');
INSERT INTO django_migrations VALUES(10,'auth','0008_alter_user_username_max_length','2024-12-17 12:37:01.477962');
INSERT INTO django_migrations VALUES(11,'auth','0009_alter_user_last_name_max_length','2024-12-17 12:37:01.477962');
INSERT INTO django_migrations VALUES(12,'auth','0010_alter_group_name_max_length','2024-12-17 12:37:01.493588');
INSERT INTO django_migrations VALUES(13,'auth','0011_update_proxy_permissions','2024-12-17 12:37:01.493588');
INSERT INTO django_migrations VALUES(14,'auth','0012_alter_user_first_name_max_length','2024-12-17 12:37:01.506596');
INSERT INTO django_migrations VALUES(15,'myapp','0001_initial','2024-12-17 12:37:01.525428');
INSERT INTO django_migrations VALUES(16,'admin','0001_initial','2024-12-17 12:37:01.535436');
INSERT INTO django_migrations VALUES(17,'admin','0002_logentry_remove_auto_add','2024-12-17 12:37:01.540942');
INSERT INTO django_migrations VALUES(18,'admin','0003_logentry_add_action_flag_choices','2024-12-17 12:37:01.540942');
INSERT INTO django_migrations VALUES(19,'sessions','0001_initial','2024-12-17 12:37:01.540942');
INSERT INTO django_migrations VALUES(20,'myapp','0002_voucher_delete_customuser','2024-12-19 08:34:53.563282');
CREATE TABLE IF NOT EXISTS "django_content_type" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "app_label" varchar(100) NOT NULL, "model" varchar(100) NOT NULL);
INSERT INTO django_content_type VALUES(1,'myapp','customuser');
INSERT INTO django_content_type VALUES(2,'admin','logentry');
INSERT INTO django_content_type VALUES(3,'auth','permission');
INSERT INTO django_content_type VALUES(4,'auth','group');
INSERT INTO django_content_type VALUES(5,'contenttypes','contenttype');
INSERT INTO django_content_type VALUES(6,'sessions','session');
INSERT INTO django_content_type VALUES(7,'auth','user');
INSERT INTO django_content_type VALUES(8,'myapp','voucher');
CREATE TABLE IF NOT EXISTS "auth_group_permissions" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "group_id" integer NOT NULL REFERENCES "auth_group" ("id") DEFERRABLE INITIALLY DEFERRED, "permission_id" integer NOT NULL REFERENCES "auth_permission" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE IF NOT EXISTS "auth_permission" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "content_type_id" integer NOT NULL REFERENCES "django_content_type" ("id") DEFERRABLE INITIALLY DEFERRED, "codename" varchar(100) NOT NULL, "name" varchar(255) NOT NULL);
INSERT INTO auth_permission VALUES(1,1,'add_customuser','Can add custom user');
INSERT INTO auth_permission VALUES(2,1,'change_customuser','Can change custom user');
INSERT INTO auth_permission VALUES(3,1,'delete_customuser','Can delete custom user');
INSERT INTO auth_permission VALUES(4,1,'view_customuser','Can view custom user');
INSERT INTO auth_permission VALUES(5,2,'add_logentry','Can add log entry');
INSERT INTO auth_permission VALUES(6,2,'change_logentry','Can change log entry');
INSERT INTO auth_permission VALUES(7,2,'delete_logentry','Can delete log entry');
INSERT INTO auth_permission VALUES(8,2,'view_logentry','Can view log entry');
INSERT INTO auth_permission VALUES(9,3,'add_permission','Can add permission');
INSERT INTO auth_permission VALUES(10,3,'change_permission','Can change permission');
INSERT INTO auth_permission VALUES(11,3,'delete_permission','Can delete permission');
INSERT INTO auth_permission VALUES(12,3,'view_permission','Can view permission');
INSERT INTO auth_permission VALUES(13,4,'add_group','Can add group');
INSERT INTO auth_permission VALUES(14,4,'change_group','Can change group');
INSERT INTO auth_permission VALUES(15,4,'delete_group','Can delete group');
INSERT INTO auth_permission VALUES(16,4,'view_group','Can view group');
INSERT INTO auth_permission VALUES(17,5,'add_contenttype','Can add content type');
INSERT INTO auth_permission VALUES(18,5,'change_contenttype','Can change content type');
INSERT INTO auth_permission VALUES(19,5,'delete_contenttype','Can delete content type');
INSERT INTO auth_permission VALUES(20,5,'view_contenttype','Can view content type');
INSERT INTO auth_permission VALUES(21,6,'add_session','Can add session');
INSERT INTO auth_permission VALUES(22,6,'change_session','Can change session');
INSERT INTO auth_permission VALUES(23,6,'delete_session','Can delete session');
INSERT INTO auth_permission VALUES(24,6,'view_session','Can view session');
INSERT INTO auth_permission VALUES(25,7,'add_user','Can add user');
INSERT INTO auth_permission VALUES(26,7,'change_user','Can change user');
INSERT INTO auth_permission VALUES(27,7,'delete_user','Can delete user');
INSERT INTO auth_permission VALUES(28,7,'view_user','Can view user');
INSERT INTO auth_permission VALUES(29,8,'add_voucher','Can add voucher');
INSERT INTO auth_permission VALUES(30,8,'change_voucher','Can change voucher');
INSERT INTO auth_permission VALUES(31,8,'delete_voucher','Can delete voucher');
INSERT INTO auth_permission VALUES(32,8,'view_voucher','Can view voucher');
CREATE TABLE IF NOT EXISTS "auth_group" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "name" varchar(150) NOT NULL UNIQUE);
CREATE TABLE IF NOT EXISTS "myapp_customuser" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "password" varchar(128) NOT NULL, "last_login" datetime NULL, "is_superuser" bool NOT NULL, "email" varchar(254) NOT NULL UNIQUE, "is_staff" bool NOT NULL, "is_active" bool NOT NULL, "date_joined" datetime NOT NULL);
CREATE TABLE IF NOT EXISTS "myapp_customuser_groups" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "customuser_id" bigint NOT NULL REFERENCES "myapp_customuser" ("id") DEFERRABLE INITIALLY DEFERRED, "group_id" integer NOT NULL REFERENCES "auth_group" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE IF NOT EXISTS "myapp_customuser_user_permissions" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "customuser_id" bigint NOT NULL REFERENCES "myapp_customuser" ("id") DEFERRABLE INITIALLY DEFERRED, "permission_id" integer NOT NULL REFERENCES "auth_permission" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE IF NOT EXISTS "django_admin_log" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "object_id" text NULL, "object_repr" varchar(200) NOT NULL, "action_flag" smallint unsigned NOT NULL CHECK ("action_flag" >= 0), "change_message" text NOT NULL, "content_type_id" integer NULL REFERENCES "django_content_type" ("id") DEFERRABLE INITIALLY DEFERRED, "user_id" bigint NOT NULL REFERENCES "myapp_customuser" ("id") DEFERRABLE INITIALLY DEFERRED, "action_time" datetime NOT NULL);
CREATE TABLE IF NOT EXISTS "django_session" ("session_key" varchar(40) NOT NULL PRIMARY KEY, "session_data" text NOT NULL, "expire_date" datetime NOT NULL);
INSERT INTO django_session VALUES('iqcvchu8hj86mp6sylbra2j0kueda549','e30:1tNpZp:7WoQuq9WYsFj9KlvvoPnOH5H5v3LWHNGJHklSy0FIys','2025-01-01 08:38:41.985454');
INSERT INTO django_session VALUES('pwxb4geyac05upmbzzz8r78zg9cffl27','e30:1tNphV:uj3YKWwLKbdSLGpmaTE1gm-GJbi1Y_OMPz8cC6yU0mY','2025-01-01 08:46:37.375878');
INSERT INTO django_session VALUES('7ncwyb0b2gkm7nzbzerhe5beuurw49b0','eyJ1c2VybmFtZSI6Im1hbGxpIn0:1tYHdR:KFPveFTyASwVkdmvCLunzQBMPe7gtkZdGj7d080TwiY','2025-01-30 04:37:37.121480');
CREATE TABLE Users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    is_admin BOOLEAN DEFAULT 1,
    is_active BOOLEAN DEFAULT 1
, PSID INTEGER);
INSERT INTO Users VALUES(17,'malli','mypassword123','malli@gmail.com','2024-12-27 17:48:02.937020','2024-12-27 17:48:02.937020',1,1,NULL);
INSERT INTO Users VALUES(78,'venkat','','venkat@gmail.com','2025-01-09 17:43:06.238565','2025-01-09 17:43:06.238565',0,0,NULL);
INSERT INTO Users VALUES(99,'raziya','mypassword123','raziya@gmail.com','2025-01-15 10:46:35.057895','2025-01-15 10:46:35.057895',0,1,10821286);
INSERT INTO Users VALUES(100,'navaneetha','mypassword123','navaneetha@gmail.com','2025-01-15 10:46:35.057895','2025-01-15 10:46:35.057895',0,1,10823415);
INSERT INTO Users VALUES(101,'shaik riaz','mypassword123','shaik@gmail.com','2025-01-15 10:46:35.057895','2025-01-15 10:46:35.057895',0,1,10821658);
INSERT INTO Users VALUES(102,'venkat_reddy','mypassword123','venkat_reddy@gmail.com','2025-01-15 10:46:35.057895','2025-01-15 10:46:35.057895',0,1,10713048);
INSERT INTO Users VALUES(103,'Durga','mypassword123','durga@gmail.com','2025-01-15 10:46:35.057895','2025-01-15 10:46:35.057895',0,1,10739134);
INSERT INTO Users VALUES(104,'vishupriya','mypassword123','vishupriya@gmail.com','2025-01-15 10:46:35.057895','2025-01-15 10:46:35.057895',0,1,10743833);
INSERT INTO Users VALUES(105,'srinivas','mypassword123','srinivas@gmail.com','2025-01-15 10:46:35.057895','2025-01-15 10:46:35.057895',0,1,10733460);
INSERT INTO Users VALUES(106,'hima_bindu','mypassword123','hima_bindu@gmail.com','2025-01-15 10:46:35.057895','2025-01-15 10:46:35.057895',0,1,10660036);
INSERT INTO Users VALUES(107,'dasari','mypassword123','dasari@gmail.com','2025-01-15 10:46:35.057895','2025-01-15 10:46:35.057895',0,1,10667525);
INSERT INTO Users VALUES(108,'suma','mypassword123','suma@gmail.com','2025-01-15 10:46:35.057895','2025-01-15 10:46:35.057895',0,1,10679227);
CREATE TABLE IF NOT EXISTS "vouchers" (
	"certification_name"	VARCHAR(255) NOT NULL,
	"voucher_code"	NVARCHAR(50) NOT NULL,
	"expiration_date"	DATE NOT NULL,
	"PSID"	NVARCHAR(50) DEFAULT NULL,
	"is_active"	BOOLEAN DEFAULT 1,
	"update_time"	TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	"discount_percentage"	INT,
	PRIMARY KEY("voucher_code")
);
INSERT INTO vouchers VALUES('AWS','AWS-001','31-12-2024',NULL,1,'2025-01-15 05:17:15',50);
INSERT INTO vouchers VALUES('AWS','AWS-002','01-01-2025',NULL,1,'2025-01-15 05:17:15',50);
INSERT INTO vouchers VALUES('AWS','AWS-003','02-01-2025',NULL,1,'2025-01-15 05:17:15',50);
INSERT INTO vouchers VALUES('AWS','AWS-004','03-01-2025',NULL,1,'2025-01-15 05:17:15',50);
INSERT INTO vouchers VALUES('AWS','AWS-005','04-01-2025',NULL,1,'2025-01-15 05:17:15',50);
INSERT INTO vouchers VALUES('AWS','AWS-006','05-01-2025',NULL,1,'2025-01-15 05:17:15',50);
INSERT INTO vouchers VALUES('AWS','AWS-007','06-01-2025',NULL,1,'2025-01-15 05:17:15',50);
INSERT INTO vouchers VALUES('AWS','AWS-008','07-01-2025',NULL,1,'2025-01-15 05:17:15',50);
INSERT INTO vouchers VALUES('AWS','AWS-009','08-01-2025',NULL,1,'2025-01-15 05:17:15',50);
INSERT INTO vouchers VALUES('AWS','AWS-010','09-01-2025',NULL,1,'2025-01-15 05:17:15',50);
INSERT INTO vouchers VALUES('AWS','AWS-011','10-01-2025',NULL,1,'2025-01-15 05:17:15',50);
INSERT INTO vouchers VALUES('AWS','AWS-012','11-01-2025',NULL,1,'2025-01-15 05:17:15',50);
INSERT INTO vouchers VALUES('AWS','AWS-013','12-01-2025',NULL,1,'2025-01-15 05:17:15',50);
INSERT INTO vouchers VALUES('AWS','AWS-014','13-01-2025',NULL,1,'2025-01-15 05:17:15',50);
INSERT INTO vouchers VALUES('AWS','AWS-015','14-01-2025',NULL,1,'2025-01-15 05:17:15',50);
INSERT INTO vouchers VALUES('AWS','AWS-016','15-01-2025',NULL,1,'2025-01-15 05:17:15',50);
INSERT INTO vouchers VALUES('AZURE','AZURE-001','31-12-2024',NULL,1,'2025-01-15 05:17:15',0);
INSERT INTO vouchers VALUES('AZURE','AZURE-002','01-01-2025',NULL,1,'2025-01-15 05:17:15',0);
INSERT INTO vouchers VALUES('AZURE','AZURE-005','04-01-2025',NULL,1,'2025-01-15 05:17:15',0);
INSERT INTO vouchers VALUES('AZURE','AZURE-006','05-01-2025',NULL,1,'2025-01-15 05:17:15',0);
INSERT INTO vouchers VALUES('AZURE','AZURE-007','06-01-2025',NULL,1,'2025-01-15 05:17:15',0);
INSERT INTO vouchers VALUES('AZURE','AZURE-008','07-01-2025',NULL,1,'2025-01-15 05:17:15',0);
INSERT INTO vouchers VALUES('AZURE','AZURE-011','10-01-2025',NULL,1,'2025-01-15 05:17:15',0);
INSERT INTO vouchers VALUES('AZURE','AZURE-012','11-01-2025',NULL,1,'2025-01-15 05:17:15',0);
INSERT INTO vouchers VALUES('AZURE','AZURE-013','12-01-2025',NULL,1,'2025-01-15 05:17:15',0);
INSERT INTO vouchers VALUES('AZURE','AZURE-014','13-01-2025',NULL,1,'2025-01-15 05:17:15',0);
INSERT INTO vouchers VALUES('AZURE','AZURE-015','14-01-2025',NULL,1,'2025-01-15 05:17:15',0);
INSERT INTO vouchers VALUES('AZURE','AZURE-016','15-01-2025',NULL,1,'2025-01-15 05:17:15',0);
INSERT INTO vouchers VALUES('AZURE','AZURE-017','16-01-2025',NULL,1,'2025-01-15 05:17:15',0);
INSERT INTO vouchers VALUES('AZURE','AZURE-018','17-01-2025',NULL,1,'2025-01-15 05:17:15',0);
INSERT INTO vouchers VALUES('GCP','GCP-001','31-12-2024',NULL,1,'2025-01-15 05:17:15',0);
INSERT INTO vouchers VALUES('GCP','GCP-002','01-01-2025',NULL,1,'2025-01-15 05:17:15',100);
INSERT INTO vouchers VALUES('GCP','GCP-003','02-01-2025',NULL,1,'2025-01-15 05:17:15',100);
INSERT INTO vouchers VALUES('GCP','GCP-004','03-01-2025',NULL,1,'2025-01-15 05:17:15',100);
INSERT INTO vouchers VALUES('GCP','GCP-005','04-01-2025',NULL,1,'2025-01-15 05:17:15',100);
INSERT INTO vouchers VALUES('GCP','GCP-006','05-01-2025',NULL,1,'2025-01-15 05:17:15',100);
INSERT INTO vouchers VALUES('GCP','GCP-007','06-01-2025',NULL,1,'2025-01-15 05:17:15',100);
INSERT INTO vouchers VALUES('GCP','GCP-008','07-01-2025',NULL,1,'2025-01-15 05:17:15',100);
INSERT INTO vouchers VALUES('GCP','GCP-009','08-01-2025',NULL,1,'2025-01-15 05:17:15',100);
INSERT INTO vouchers VALUES('GCP','GCP-010','09-01-2025',NULL,1,'2025-01-15 05:17:15',100);
INSERT INTO vouchers VALUES('GCP','GCP-011','10-01-2025',NULL,1,'2025-01-15 05:17:15',100);
INSERT INTO vouchers VALUES('GCP','GCP-012','11-01-2025',NULL,1,'2025-01-15 05:17:15',100);
INSERT INTO vouchers VALUES('GCP','GCP-013','12-01-2025',NULL,1,'2025-01-15 05:17:15',100);
INSERT INTO vouchers VALUES('GCP','GCP-014','13-01-2025',NULL,1,'2025-01-15 05:17:15',100);
INSERT INTO vouchers VALUES('GCP','GCP-015','14-01-2025',NULL,1,'2025-01-15 05:17:15',100);
INSERT INTO vouchers VALUES('GCP','GCP-016','15-01-2025',NULL,1,'2025-01-15 05:17:15',100);
INSERT INTO vouchers VALUES('GCP','GCP-017','16-01-2025',NULL,1,'2025-01-15 05:17:15',100);
INSERT INTO vouchers VALUES('GCP','GCP-018','17-01-2025',NULL,1,'2025-01-15 05:17:15',100);
INSERT INTO vouchers VALUES('GCP','GCP-019','18-01-2025',NULL,1,'2025-01-15 05:17:15',100);
INSERT INTO vouchers VALUES('GCP','GCP-020','19-01-2025',NULL,1,'2025-01-15 05:17:15',100);
CREATE TABLE IF NOT EXISTS "certification" (
	"id"	INTEGER,
	"Name"	VARCHAR(255) NOT NULL,
	"Provider"	VARCHAR(255) NOT NULL,
	"Status"	VARCHAR(50) NOT NULL
);
INSERT INTO certification VALUES('1Z0-071',' ORACLE DATABASE SQL','ORACLE','active');
INSERT INTO certification VALUES('1Z0-082','Oracle database administration professional 2020','ORACLE','active');
INSERT INTO certification VALUES('A00-250','SAS Platform Administration for SAS 10','SAS','active');
INSERT INTO certification VALUES('ADOBE-114','Adobe Analytics Developer','Adobe','inactive');
INSERT INTO certification VALUES('ADOBEBU-1056','Adobe Audience Manager Business Practitioner Certification','Adobe','active');
INSERT INTO certification VALUES('AEM-1905','Adobe Certified Professional - AEM Developer','Adobe','inactive');
INSERT INTO certification VALUES('ADOBE-114','Adobe Experience Platform Developer','Adobe','active');
INSERT INTO certification VALUES('AWS-1002','AWS Certified AI Practitioner','AMAZON','active');
INSERT INTO certification VALUES('AWS-1105','AWS Certified Cloud Practitioner','AMAZON','active');
INSERT INTO certification VALUES('AWS-1408','AWS Certified Data Analytics - Specialty','AMAZON','inactive');
INSERT INTO certification VALUES('AWS-1408','AWS Certified Data Engineer - Associate','AMAZON','active');
INSERT INTO certification VALUES('AWS-1681','AWS Certified Database - Specialty','AMAZON','active');
INSERT INTO certification VALUES('AWS-1680','AWS Certified Developer - Associate','AMAZON','inactive');
INSERT INTO certification VALUES('AWS-1679','AWS Certified DevOps Engineer – Professional','AMAZON','active');
INSERT INTO certification VALUES('AWS-1678','AWS Certified Machine Learning - Specialty','AMAZON','active');
INSERT INTO certification VALUES('AWS-1677','AWS Certified Security – Specialty','AMAZON','active');
INSERT INTO certification VALUES('AWS-1408','AWS Certified Solutions Architect - Associate','AMAZON','inactive');
INSERT INTO certification VALUES('AWS-1408','AWS Certified Solutions Architect - Professional','AMAZON','inactive');
INSERT INTO certification VALUES('AWS-1105','AWS Certified SysOps Administrator - Associate','AMAZON','active');
INSERT INTO certification VALUES('AWS-1105','AWS Partner: Cloud Economics','AMAZON','inactive');
INSERT INTO certification VALUES('AWS-1408','AWS Partner: Cloud Economics Accreditation','AMAZON','inactive');
INSERT INTO certification VALUES('AWS-1408','AWS Partner: Sales Accreditation (Business)','AMAZON','active');
CREATE TABLE IF NOT EXISTS "employeecertifications" (
	"id"	integer NOT NULL,
	"employee_name"	varchar(100) NOT NULL,
	"employee_ps_no"	integer NOT NULL,
	"employee_designation"	varchar(50) NOT NULL,
	"certification_name"	varchar(50) NOT NULL,
	"certification_status"	varchar(50) NOT NULL,
	"exam_date"	date,
	"update_date"	datetime,
	"uploaded_certificate"	varchar(100),
	PRIMARY KEY("id" AUTOINCREMENT)
);
INSERT INTO employeecertifications VALUES(1,'Suresh',10821336,'Senior Specialist','AWS','WCP pending','12-12-2025','','');
INSERT INTO employeecertifications VALUES(2,'Ramesh',10821335,'Senior Specialist','AZURE','WCP pending','12-12-2025','','');
INSERT INTO employeecertifications VALUES(3,'Navaneetha',10821340,'Senior Specialist Data Engineering','SNOWFLAKe','WCP pending','12-05-2025','','');
INSERT INTO sqlite_sequence VALUES('django_migrations',20);
INSERT INTO sqlite_sequence VALUES('django_content_type',8);
INSERT INTO sqlite_sequence VALUES('auth_permission',32);
INSERT INTO sqlite_sequence VALUES('auth_group',0);
INSERT INTO sqlite_sequence VALUES('django_admin_log',0);
INSERT INTO sqlite_sequence VALUES('Users',108);
INSERT INTO sqlite_sequence VALUES('employeecertifications',3);
CREATE UNIQUE INDEX "django_content_type_app_label_model_76bd3d3b_uniq" ON "django_content_type" ("app_label", "model");
CREATE UNIQUE INDEX "auth_group_permissions_group_id_permission_id_0cd325b0_uniq" ON "auth_group_permissions" ("group_id", "permission_id");
CREATE INDEX "auth_group_permissions_group_id_b120cbf9" ON "auth_group_permissions" ("group_id");
CREATE INDEX "auth_group_permissions_permission_id_84c5c92e" ON "auth_group_permissions" ("permission_id");
CREATE UNIQUE INDEX "auth_permission_content_type_id_codename_01ab375a_uniq" ON "auth_permission" ("content_type_id", "codename");
CREATE INDEX "auth_permission_content_type_id_2f476e4b" ON "auth_permission" ("content_type_id");
CREATE UNIQUE INDEX "myapp_customuser_groups_customuser_id_group_id_8dfb17af_uniq" ON "myapp_customuser_groups" ("customuser_id", "group_id");
CREATE INDEX "myapp_customuser_groups_customuser_id_4b46b787" ON "myapp_customuser_groups" ("customuser_id");
CREATE INDEX "myapp_customuser_groups_group_id_9a436a56" ON "myapp_customuser_groups" ("group_id");
CREATE UNIQUE INDEX "myapp_customuser_user_permissions_customuser_id_permission_id_a9e136bb_uniq" ON "myapp_customuser_user_permissions" ("customuser_id", "permission_id");
CREATE INDEX "myapp_customuser_user_permissions_customuser_id_afabd7b0" ON "myapp_customuser_user_permissions" ("customuser_id");
CREATE INDEX "myapp_customuser_user_permissions_permission_id_4ffda77e" ON "myapp_customuser_user_permissions" ("permission_id");
CREATE INDEX "django_admin_log_content_type_id_c4bce8eb" ON "django_admin_log" ("content_type_id");
CREATE INDEX "django_admin_log_user_id_c564eba6" ON "django_admin_log" ("user_id");
CREATE INDEX "django_session_expire_date_a5c62663" ON "django_session" ("expire_date");
COMMIT;
