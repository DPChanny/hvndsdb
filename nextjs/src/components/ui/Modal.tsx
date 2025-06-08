import { cn } from "@/lib/utils";
import styles from "@/styles/components/ui/Modal.module.css";
import { cva, type VariantProps } from "class-variance-authority";
import React from "react";

const modalVariants = cva(styles.modal, {
  variants: {
    tone: {
      solid: styles["modal--solid"],
      ghost: styles["modal--ghost"],
      outline: styles["modal--outline"],
    },
    size: {
      sm: styles["modal--sm"],
      md: styles["modal--md"],
      lg: styles["modal--lg"],
    },
  },
  defaultVariants: {
    tone: "solid",
    size: "md",
  },
});

export type ModalProps = {
  open: boolean;
  onClose: () => void;
  children: React.ReactNode;
  className?: string;
  variantTone?: VariantProps<typeof modalVariants>["tone"];
  variantSize?: VariantProps<typeof modalVariants>["size"];
};

export const Modal = ({
  open,
  onClose,
  children,
  className,
  variantTone,
  variantSize,
}: ModalProps) => {
  if (!open) return null;

  return (
    <div className={styles.overlay} onClick={onClose}>
      <div
        className={cn(
          modalVariants({ tone: variantTone, size: variantSize }),
          className
        )}
        onClick={(e) => e.stopPropagation()}
      >
        <button className={styles.closeButton} onClick={onClose}>
          &times;
        </button>
        {children}
      </div>
    </div>
  );
};
