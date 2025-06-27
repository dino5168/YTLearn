-- 1. 角色表（Role）
CREATE TABLE roles (
id INTEGER PRIMARY KEY AUTOINCREMENT,
name TEXT NOT NULL UNIQUE, -- 角色中文名稱
key TEXT NOT NULL UNIQUE, -- 角色系統識別碼（如 "teacher"）
description TEXT -- 角色描述
);

-- 2. 主選單表（NavItem）
CREATE TABLE nav_items (
id INTEGER PRIMARY KEY AUTOINCREMENT,
label TEXT NOT NULL, -- 主選單名稱
href TEXT -- 主選單連結，可為 NULL（若有 dropdown）
);

-- 3. 子選單表（NavDropdown）
CREATE TABLE nav_dropdowns (
id INTEGER PRIMARY KEY AUTOINCREMENT,
nav_item_id INTEGER NOT NULL, -- 所屬主選單
label TEXT NOT NULL, -- 子選單名稱
href TEXT NOT NULL, -- 子選單連結
FOREIGN KEY (nav_item_id) REFERENCES nav_items(id) ON DELETE CASCADE
);

-- 4. 多對多：主選單可見角色對應表
CREATE TABLE nav_items_roles (
nav_item_id INTEGER NOT NULL,
role_id INTEGER NOT NULL,
PRIMARY KEY (nav_item_id, role_id),
FOREIGN KEY (nav_item_id) REFERENCES nav_items(id) ON DELETE CASCADE,
FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE CASCADE
);

-- 5. 多對多：子選單可見角色對應表
CREATE TABLE nav_dropdowns_roles (
nav_dropdown_id INTEGER NOT NULL,
role_id INTEGER NOT NULL,
PRIMARY KEY (nav_dropdown_id, role_id),
FOREIGN KEY (nav_dropdown_id) REFERENCES nav_dropdowns(id) ON DELETE CASCADE,
FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE CASCADE
);
