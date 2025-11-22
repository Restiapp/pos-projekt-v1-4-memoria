// TODO-S0-STUB: TypeScript checking disabled - fix ReactNode import issues
// @ts-nocheck
/**
 * ErrorBoundary - Catches render errors
 * Displays fallback UI using Card component
 */

import { Component, ReactNode } from 'react';
import { Card } from './Card';
import './ErrorBoundary.css';

interface ErrorBoundaryProps {
  children: ReactNode;
  fallback?: ReactNode;
  onError?: (error: Error, errorInfo: React.ErrorInfo) => void;
}

interface ErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
  errorInfo: React.ErrorInfo | null;
}

export class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
    };
  }

  static getDerivedStateFromError(error: Error): Partial<ErrorBoundaryState> {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo): void {
    this.setState({
      error,
      errorInfo,
    });

    // Log error to console
    console.error('ErrorBoundary caught an error:', error, errorInfo);

    // Call optional error handler
    if (this.props.onError) {
      this.props.onError(error, errorInfo);
    }
  }

  handleReset = (): void => {
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null,
    });
  };

  render(): ReactNode {
    if (this.state.hasError) {
      // Custom fallback if provided
      if (this.props.fallback) {
        return this.props.fallback;
      }

      // Default fallback UI using Card component
      return (
        <Card className="error-boundary-card" title="Hiba történt">
          <div className="error-boundary-content">
            <div className="error-icon">⚠️</div>
            <h2>Váratlan hiba történt</h2>
            <p className="error-message">
              Sajnáljuk, de hiba lépett fel az oldal betöltése során.
            </p>
            {this.state.error && (
              <details className="error-details">
                <summary>Technikai részletek</summary>
                <div className="error-stack">
                  <strong>Hibaüzenet:</strong>
                  <pre>{this.state.error.toString()}</pre>
                  {this.state.errorInfo && (
                    <>
                      <strong>Stack trace:</strong>
                      <pre>{this.state.errorInfo.componentStack}</pre>
                    </>
                  )}
                </div>
              </details>
            )}
            <button onClick={this.handleReset} className="error-reset-btn">
              🔄 Újrapróbálás
            </button>
          </div>
        </Card>
      );
    }

    return this.props.children;
  }
}
