import React from 'react';
import './Card.css';

/**
 * Props do Card
 * Estende HTMLAttributes<HTMLDivElement> para aceitar onClick, style, id, etc.
 */
interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
  className?: string; // Permite adicionar classes extras (ex: 'metric-card')
  noPadding?: boolean; // Opção para remover padding interno se necessário
}

export const Card = ({ 
  children, 
  className = '', 
  noPadding = false, 
  ...props 
}: CardProps) => {
  // Combina a classe base 'card' com as classes passadas via props
  const classes = `card ${noPadding ? 'card-no-padding' : ''} ${className}`;

  return (
    <div className={classes} {...props}>
      {children}
    </div>
  );
};