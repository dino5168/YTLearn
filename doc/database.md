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

-- 使用者與角色的多對多關聯表
CREATE TABLE user_roles (
user_id INTEGER NOT NULL,
role_id INTEGER NOT NULL,
PRIMARY KEY (user_id, role_id),
FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE CASCADE
);

-- Table: public.users

-- DROP TABLE IF EXISTS public.users;

CREATE TABLE IF NOT EXISTS public.users
(
id integer NOT NULL DEFAULT nextval('users_id_seq'::regclass),
email text COLLATE pg_catalog."default" NOT NULL,
name text COLLATE pg_catalog."default",
avatar_url text COLLATE pg_catalog."default",
google_id text COLLATE pg_catalog."default",
created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
is_active boolean DEFAULT true,
role_id integer,
CONSTRAINT users_pkey PRIMARY KEY (id),
CONSTRAINT users_email_key UNIQUE (email),
CONSTRAINT users_role_id_fkey FOREIGN KEY (role_id)
REFERENCES public.roles (id) MATCH SIMPLE
ON UPDATE NO ACTION
ON DELETE NO ACTION
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.users
OWNER to postgres;

COMMENT ON COLUMN public.users.id
IS '識別子';

COMMENT ON COLUMN public.users.email
IS '電子郵件';

COMMENT ON COLUMN public.users.name
IS '使用者名稱';

COMMENT ON COLUMN public.users.avatar_url
IS 'Google 頭像';

COMMENT ON COLUMN public.users.google_id
IS 'Google 給的 ID';

COMMENT ON COLUMN public.users.created_at
IS '建立日期';

COMMENT ON COLUMN public.users.updated_at
IS '修改日期';

COMMENT ON COLUMN public.users.is_active
IS '是否使用';

COMMENT ON COLUMN public.users.role_id
IS '使用者角色 ID，為 NULL 表示訪客';
