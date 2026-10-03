# task 1
passwords = ["password123", "Qwerty!2023", "admin", "MyP@ssw0rd", "123456",
             "SecurePass!", "test", "P@ssw0rd123", "welcome", "StrongP@ss1"]
criteria = {"min_length": 8, "require_digits": True, "require_upper": True,
            "require_special": True}
forbidden_passwords = {"password", "123456", "admin", "test", "welcome",
            "qwerty"}

# task 2
users = {
"admin001": {"role": "administrator", "clearance": 4, "department": "IT",
"active": True},
"user123": {"role": "analyst", "clearance": 2, "department": "Security",
"active": True},
"guest789": {"role": "guest", "clearance": 1, "department": "External",
"active": True},
"manager456": {"role": "manager", "clearance": 3, "department":
"Operations", "active": True},
"contractor99": {"role": "contractor", "clearance": 1, "department":
"External", "active": False}
}
resources = [("database_backup", 4), ("user_logs", 2), ("public_docs", 1),
("financial_reports", 3), ("system_config", 4), ("training_materials", 1),
("security_policies", 3), ("audit_logs", 4), ("employee_data", 3),
("temp_files", 1)]
security_levels = ("Public", "Internal", "Confidential", "Secret")
blocked_users = {"contractor99", "temp_user", "suspended_acc"}

# task 3
USERS_TO_REGISTER = (
    ("admin_root", "UltraSecur3#Pass2026!"),
    ("sec_analyst", "Analyst_P@ssw0rd#12"),
    ("soc_operator", "SOC_M0nit0ring#2026"),
    ("net_engineer", "Switch_R0ut3r_C0nfig!"),
    ("dev_sec_ops", "Pip3lin3_Secur1ty#99"),
    ("incident_mgr", "Resp0ns3_Pl@n_2026!"),
    ("audit_lead", "C0mplianc3_Ch3ck#321"),
    ("crypto_guru", "EllipticCurv3_K3y#8"),
    ("malware_tech", "Rev3rs3_Engin33r#77"),
    ("guest_tester", "Temp_G阳光st#V@lid12"),
)