import React, { ReactNode } from 'react';

interface CardProps {
    children: ReactNode;
    className?: string;
}

export function Card({ children, className = '', ...props }: CardProps) {
    return (
        <div className={`border p-4 rounded ${className}`} {...props}>
            {children}
        </div>
    );
}

export function CardContent({ children, ...props }: CardProps) {
    return <div {...props}>{children}</div>;
}
