import logoImg from '../assets/logo.png';

interface LogoProps {
  className?: string;
}

export default function Logo({ className = '' }: LogoProps) {
  return (
    <div className={`flex items-center ${className}`}>
      <img
        src={logoImg}
        alt="Company Logo"
        className="h-8 w-auto"
        style={{ filter: 'brightness(0) invert(1)' }}
      />
    </div>
  );
}
