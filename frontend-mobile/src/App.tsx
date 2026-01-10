import React from 'react';
import { AuthProvider } from './context/AuthContext';
import { ProductsProvider } from './context/ProductsContext';
import { MovementsProvider } from './context/MovementsContext';
import { UsersProvider } from './context/UsersContext';
import { KpisProvider } from './context/KpisContext';
import { AppRouter } from './navigation/AppRouter';

export const App = () => 

<AuthProvider>
  <ProductsProvider>
    <MovementsProvider>
      <UsersProvider>
        <KpisProvider>
          <AppRouter />
        </KpisProvider>
      </UsersProvider>
    </MovementsProvider>
  </ProductsProvider>
</AuthProvider>