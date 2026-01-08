








Estrutura de pastas do projeto:

logistiq-2.0/
│
├── backend/                  # FastAPI backend
│   ├── app/
│   │   ├── models.py
│   │   ├── schemas.py
│   │   ├── routes/
│   │   │   ├── auth.py
│   │   │   ├── users.py
│   │   │   ├── products.py
│   │   │   └── movements.py
│   │   ├── core/
│   │   │   ├── security.py
│   │   │   └── roles.py
│   │   └── main.py
│   └── requirements.txt
│
├── frontend-web/
│   ├── src/
│   │   ├── api/               # Axios + AuthInterceptor
│   │   │   ├── client.ts
│   │   │   └── endpoints.ts
│   │   ├── components/        # UI reutilizável
│   │   │   ├── Button/
│   │   │   ├── Input/
│   │   │   └── Card/
│   │   ├── context/
│   │   │   ├── AuthContext.tsx
│   │   │   ├── ProductsContext.tsx
│   │   │   └── MovementsContext.tsx
│   │   ├── hooks/
│   │   │   ├── useAuth.ts
│   │   │   ├── useProducts.ts
│   │   │   └── useMovements.ts
│   │   ├── pages/
│   │   │   ├── Login/
│   │   │   ├── Dashboard/
│   │   │   ├── Products/
│   │   │   └── Movements/
│   │   ├── navigation/
│   │   │   └── AppRouter.tsx
│   │   ├── utils/
│   │   └── App.tsx
│   └── package.json
│
├── frontend-mobile/
│   ├── src/
│   │   ├── api/               # Axios + AuthInterceptor compartilhável
│   │   │   ├── client.ts
│   │   │   └── endpoints.ts
│   │   ├── components/        # UI reutilizável (Buttons, Inputs, Cards)
│   │   ├── context/           # AuthContext, ProductsContext, MovementsContext
│   │   ├── hooks/             # useAuth, useProducts, useMovements
│   │   ├── screens/           # Login, Dashboard, Products, Movements
│   │   ├── navigation/
│   │   │   └── AppNavigator.tsx
│   │   ├── utils/
│   │   └── App.tsx
│   └── package.json
│
└── README.md
