[users] ─────┐
└─(多對一)─► [roles]
▲ │
(多對多) │ └─(多對多)─► [role_nav_items] ◄─► [nav_items]
[users_roles] │
└─(一對多)─► [nav_dropdowns]
▲
[role_nav_dropdowns] ◄─(多對多)─ [roles]
