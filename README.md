# EDMMS — Executive & Departmental Meeting Management System

Public testing copy. Original private repo: https://github.com/salemaldhaheri197-stack/edmms

**Classification:** Reference implementation aligned to BRD/SRS v4.0  
**Languages:** Arabic (RTL) + English (LTR)

This repository is a security-aware reference platform, not a certified national-defense deployment.

## Quick start

```bash
git clone https://github.com/salemaldhaheri197-stack/edmms-public.git
cd edmms-public
cp .env.example .env
docker compose up --build
```

- API: http://localhost:8080/docs
- Console: http://localhost:5173

Dev seed password for all demo users: `ChangeMe!2026`
Users: ceo (TOP_SECRET), vp.ops (SECRET), ea.ceo (SECRET), manager.it (CONFIDENTIAL), analyst (RESTRICTED), soc.admin (SECRET)
