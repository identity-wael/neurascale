import React, { ButtonHTMLAttributes, DetailedHTMLProps, ReactNode } from 'react';

interface ButtonProps extends DetailedHTMLProps<ButtonHTMLAttributes<HTMLButtonElement>, HTMLButtonElement> {
    children: ReactNode;
    className?: string;
    variant?: 'primary' | 'secondary' | 'outline';
    size?: 'sm' | 'md' | 'lg';
}

export function Button({ children, className = '', variant = 'primary', size = 'md', ...props }: ButtonProps) {
    const variantClass = {
        primary: 'bg-blue-500 text-white',
        secondary: 'bg-gray-500 text-white',
        outline: 'border border-gray-500 text-gray-500',
    }[variant];

    const sizeClass = {
        sm: 'px-2 py-1 text-sm',
        md: 'px-4 py-2 text-base',
        lg: 'px-6 py-3 text-lg',
    }[size];

    return (
        <button className={`rounded ${variantClass} ${sizeClass} ${className}`} {...props}>
            {children}
        </button>
    );
}