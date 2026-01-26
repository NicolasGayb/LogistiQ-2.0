import React from 'react';
import './Button.css';

/**
 * Variantes visuais do botão
 */
type ButtonVariant = 'primary' | 'secondary' | 'outline' | 'ghost' | 'danger';
type ButtonSize = 'sm' | 'md' | 'lg';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  children: React.ReactNode;
  variant?: ButtonVariant;
  size?: ButtonSize;
  isLoading?: boolean; // Estado de carregamento
  leftIcon?: React.ReactNode; // Ícone opcional à esquerda
}

export const Button = ({
  children,
  className = '',
  variant = 'primary',
  size = 'md',
  isLoading = false,
  leftIcon,
  disabled,
  ...props
}: ButtonProps) => {
  
  // Montagem dinâmica das classes CSS
  const classes = `
    btn 
    btn-${variant} 
    btn-${size} 
    ${isLoading ? 'btn-loading' : ''} 
    ${className}
  `.trim();

  return (
    <button 
      className={classes} 
      disabled={disabled || isLoading} 
      {...props}
    >
      {/* Se estiver carregando, mostra spinner (opcional) ou texto de loading */}
      {isLoading ? (
        <span className="btn-spinner" />
      ) : (
        <>
          {leftIcon && <span className="btn-icon">{leftIcon}</span>}
          {children}
        </>
      )}
    </button>
  );
};