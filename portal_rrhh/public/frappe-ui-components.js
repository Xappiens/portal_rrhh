/**
 * Frappe UI Components Implementation for Portal RRHH
 * Based on https://ui.frappe.io/ documentation
 */

// Frappe UI Component Library
const FrappeUI = {
  // Button Components
  Button: {
    template: `
      <button
        :class="buttonClasses"
        :disabled="disabled"
        @click="$emit('click', $event)"
        v-bind="$attrs"
      >
        <i v-if="icon" :class="icon" class="mr-2"></i>
        <slot></slot>
      </button>
    `,
    props: {
      variant: {
        type: String,
        default: 'primary',
        validator: value => ['primary', 'secondary', 'outline', 'ghost', 'danger'].includes(value)
      },
      size: {
        type: String,
        default: 'md',
        validator: value => ['xs', 'sm', 'md', 'lg', 'xl'].includes(value)
      },
      disabled: Boolean,
      loading: Boolean,
      icon: String
    },
    computed: {
      buttonClasses() {
        const baseClasses = 'inline-flex items-center justify-center font-medium rounded-lg transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2';

        const variants = {
          primary: 'bg-primary-600 text-white hover:bg-primary-700 focus:ring-primary-500',
          secondary: 'bg-gray-200 text-gray-900 hover:bg-gray-300 focus:ring-gray-500',
          outline: 'border border-gray-300 text-gray-700 hover:bg-gray-50 focus:ring-primary-500',
          ghost: 'text-gray-700 hover:bg-gray-100 focus:ring-primary-500',
          danger: 'bg-red-600 text-white hover:bg-red-700 focus:ring-red-500'
        };

        const sizes = {
          xs: 'px-2 py-1 text-xs',
          sm: 'px-3 py-1.5 text-sm',
          md: 'px-4 py-2 text-sm',
          lg: 'px-6 py-3 text-base',
          xl: 'px-8 py-4 text-lg'
        };

        const disabledClasses = this.disabled ? 'opacity-50 cursor-not-allowed' : '';

        return `${baseClasses} ${variants[this.variant]} ${sizes[this.size]} ${disabledClasses}`;
      }
    }
  },

  // Card Component
  Card: {
    template: `
      <div :class="cardClasses">
        <div v-if="$slots.header" class="px-6 py-4 border-b border-gray-200">
          <slot name="header"></slot>
        </div>
        <div class="px-6 py-4">
          <slot></slot>
        </div>
        <div v-if="$slots.footer" class="px-6 py-4 border-t border-gray-200 bg-gray-50">
          <slot name="footer"></slot>
        </div>
      </div>
    `,
    props: {
      variant: {
        type: String,
        default: 'default',
        validator: value => ['default', 'elevated', 'outlined'].includes(value)
      }
    },
    computed: {
      cardClasses() {
        const baseClasses = 'bg-white rounded-lg border';
        const variants = {
          default: 'border-gray-200 shadow-sm',
          elevated: 'border-gray-200 shadow-md',
          outlined: 'border-gray-300 shadow-none'
        };
        return `${baseClasses} ${variants[this.variant]}`;
      }
    }
  },

  // Input Component
  Input: {
    template: `
      <div class="space-y-1">
        <label v-if="label" :for="inputId" class="block text-sm font-medium text-gray-700">
          {{ label }}
          <span v-if="required" class="text-red-500">*</span>
        </label>
        <input
          :id="inputId"
          :type="type"
          :value="modelValue"
          :placeholder="placeholder"
          :disabled="disabled"
          :class="inputClasses"
          @input="$emit('update:modelValue', $event.target.value)"
          @blur="$emit('blur', $event)"
          @focus="$emit('focus', $event)"
          v-bind="$attrs"
        />
        <p v-if="error" class="text-sm text-red-600">{{ error }}</p>
        <p v-if="help" class="text-sm text-gray-500">{{ help }}</p>
      </div>
    `,
    props: {
      modelValue: [String, Number],
      type: {
        type: String,
        default: 'text'
      },
      label: String,
      placeholder: String,
      disabled: Boolean,
      required: Boolean,
      error: String,
      help: String,
      size: {
        type: String,
        default: 'md',
        validator: value => ['sm', 'md', 'lg'].includes(value)
      }
    },
    computed: {
      inputId() {
        return `input-${Math.random().toString(36).substr(2, 9)}`;
      },
      inputClasses() {
        const baseClasses = 'block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500';
        const sizes = {
          sm: 'px-3 py-1.5 text-sm',
          md: 'px-3 py-2 text-sm',
          lg: 'px-4 py-3 text-base'
        };
        const errorClasses = this.error ? 'border-red-300 focus:border-red-500 focus:ring-red-500' : '';
        const disabledClasses = this.disabled ? 'bg-gray-50 cursor-not-allowed' : '';

        return `${baseClasses} ${sizes[this.size]} ${errorClasses} ${disabledClasses}`;
      }
    }
  },

  // Table Component
  Table: {
    template: `
      <div class="overflow-hidden shadow ring-1 ring-black ring-opacity-5 md:rounded-lg">
        <table class="min-w-full divide-y divide-gray-300">
          <thead class="bg-gray-50">
            <tr>
              <th
                v-for="column in columns"
                :key="column.key"
                :class="headerClasses"
                scope="col"
              >
                {{ column.label }}
              </th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="(row, index) in data" :key="index" class="hover:bg-gray-50">
              <td
                v-for="column in columns"
                :key="column.key"
                :class="cellClasses"
              >
                <slot :name="column.key" :row="row" :value="row[column.key]">
                  {{ row[column.key] }}
                </slot>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    `,
    props: {
      data: {
        type: Array,
        default: () => []
      },
      columns: {
        type: Array,
        required: true
      }
    },
    computed: {
      headerClasses() {
        return 'px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider';
      },
      cellClasses() {
        return 'px-6 py-4 whitespace-nowrap text-sm text-gray-900';
      }
    }
  },

  // Dialog Component
  Dialog: {
    template: `
      <Teleport to="body">
        <div v-if="show" class="fixed inset-0 z-50 overflow-y-auto">
          <div class="flex min-h-screen items-center justify-center p-4">
            <div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" @click="close"></div>
            <div class="relative transform overflow-hidden rounded-lg bg-white shadow-xl transition-all">
              <div class="px-6 py-4 border-b border-gray-200">
                <h3 class="text-lg font-medium text-gray-900">{{ title }}</h3>
              </div>
              <div class="px-6 py-4">
                <slot></slot>
              </div>
              <div v-if="$slots.footer" class="px-6 py-4 border-t border-gray-200 bg-gray-50">
                <slot name="footer"></slot>
              </div>
            </div>
          </div>
        </div>
      </Teleport>
    `,
    props: {
      show: Boolean,
      title: String
    },
    emits: ['close'],
    methods: {
      close() {
        this.$emit('close');
      }
    }
  },

  // Badge Component
  Badge: {
    template: `
      <span :class="badgeClasses">
        <slot></slot>
      </span>
    `,
    props: {
      variant: {
        type: String,
        default: 'default',
        validator: value => ['default', 'primary', 'success', 'warning', 'error', 'info'].includes(value)
      },
      size: {
        type: String,
        default: 'md',
        validator: value => ['sm', 'md', 'lg'].includes(value)
      }
    },
    computed: {
      badgeClasses() {
        const baseClasses = 'inline-flex items-center font-medium rounded-full';

        const variants = {
          default: 'bg-gray-100 text-gray-800',
          primary: 'bg-primary-100 text-primary-800',
          success: 'bg-green-100 text-green-800',
          warning: 'bg-yellow-100 text-yellow-800',
          error: 'bg-red-100 text-red-800',
          info: 'bg-blue-100 text-blue-800'
        };

        const sizes = {
          sm: 'px-2 py-0.5 text-xs',
          md: 'px-2.5 py-0.5 text-sm',
          lg: 'px-3 py-1 text-sm'
        };

        return `${baseClasses} ${variants[this.variant]} ${sizes[this.size]}`;
      }
    }
  },

  // Alert Component
  Alert: {
    template: `
      <div :class="alertClasses" role="alert">
        <div class="flex">
          <div class="flex-shrink-0">
            <i :class="iconClass" class="h-5 w-5"></i>
          </div>
          <div class="ml-3">
            <h3 v-if="title" class="text-sm font-medium">{{ title }}</h3>
            <div class="mt-2 text-sm">
              <slot></slot>
            </div>
          </div>
        </div>
      </div>
    `,
    props: {
      variant: {
        type: String,
        default: 'info',
        validator: value => ['success', 'warning', 'error', 'info'].includes(value)
      },
      title: String
    },
    computed: {
      alertClasses() {
        const baseClasses = 'rounded-md p-4';
        const variants = {
          success: 'bg-green-50 border border-green-200',
          warning: 'bg-yellow-50 border border-yellow-200',
          error: 'bg-red-50 border border-red-200',
          info: 'bg-blue-50 border border-blue-200'
        };
        return `${baseClasses} ${variants[this.variant]}`;
      },
      iconClass() {
        const icons = {
          success: 'fas fa-check-circle text-green-400',
          warning: 'fas fa-exclamation-triangle text-yellow-400',
          error: 'fas fa-times-circle text-red-400',
          info: 'fas fa-info-circle text-blue-400'
        };
        return icons[this.variant];
      }
    }
  },

  // Progress Component
  Progress: {
    template: `
      <div class="w-full">
        <div class="flex justify-between text-sm font-medium text-gray-700 mb-1">
          <span>{{ label }}</span>
          <span>{{ value }}%</span>
        </div>
        <div class="w-full bg-gray-200 rounded-full h-2">
          <div
            :class="progressClasses"
            :style="{ width: value + '%' }"
          ></div>
        </div>
      </div>
    `,
    props: {
      value: {
        type: Number,
        default: 0,
        validator: value => value >= 0 && value <= 100
      },
      label: String,
      variant: {
        type: String,
        default: 'primary',
        validator: value => ['primary', 'success', 'warning', 'error'].includes(value)
      }
    },
    computed: {
      progressClasses() {
        const baseClasses = 'h-2 rounded-full transition-all duration-300';
        const variants = {
          primary: 'bg-primary-600',
          success: 'bg-green-600',
          warning: 'bg-yellow-600',
          error: 'bg-red-600'
        };
        return `${baseClasses} ${variants[this.variant]}`;
      }
    }
  },

  // Avatar Component
  Avatar: {
    template: `
      <div :class="avatarClasses">
        <img v-if="src" :src="src" :alt="alt" class="w-full h-full object-cover rounded-full" />
        <div v-else class="w-full h-full bg-gray-300 rounded-full flex items-center justify-center">
          <i class="fas fa-user text-gray-600"></i>
        </div>
      </div>
    `,
    props: {
      src: String,
      alt: String,
      size: {
        type: String,
        default: 'md',
        validator: value => ['xs', 'sm', 'md', 'lg', 'xl'].includes(value)
      }
    },
    computed: {
      avatarClasses() {
        const sizes = {
          xs: 'w-6 h-6',
          sm: 'w-8 h-8',
          md: 'w-10 h-10',
          lg: 'w-12 h-12',
          xl: 'w-16 h-16'
        };
        return `inline-block ${sizes[this.size]}`;
      }
    }
  },

  // Dropdown Component
  Dropdown: {
    template: `
      <div class="relative inline-block text-left" ref="dropdown">
        <div>
          <button
            type="button"
            :class="buttonClasses"
            @click="toggle"
            aria-expanded="open"
            aria-haspopup="true"
          >
            <slot name="trigger">
              {{ label }}
              <i class="fas fa-chevron-down ml-2"></i>
            </slot>
          </button>
        </div>
        <div
          v-if="isOpen"
          :class="menuClasses"
          role="menu"
          aria-orientation="vertical"
        >
          <slot></slot>
        </div>
      </div>
    `,
    props: {
      label: String,
      align: {
        type: String,
        default: 'left',
        validator: value => ['left', 'right'].includes(value)
      }
    },
    data() {
      return {
        isOpen: false
      };
    },
    computed: {
      buttonClasses() {
        return 'inline-flex w-full justify-center gap-x-1.5 rounded-md bg-white px-3 py-2 text-sm font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50';
      },
      menuClasses() {
        const baseClasses = 'absolute z-10 mt-2 w-56 origin-top-right rounded-md bg-white shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none';
        const alignClasses = this.align === 'right' ? 'right-0' : 'left-0';
        return `${baseClasses} ${alignClasses}`;
      }
    },
    methods: {
      toggle() {
        this.isOpen = !this.isOpen;
      },
      close() {
        this.isOpen = false;
      }
    },
    mounted() {
      document.addEventListener('click', (e) => {
        if (!this.$refs.dropdown.contains(e.target)) {
          this.close();
        }
      });
    }
  },

  // Toast Component
  Toast: {
    template: `
      <Teleport to="body">
        <Transition
          enter-active-class="transform ease-out duration-300 transition"
          enter-from-class="translate-y-2 opacity-0 sm:translate-y-0 sm:translate-x-2"
          enter-to-class="translate-y-0 opacity-100 sm:translate-x-0"
          leave-active-class="transition ease-in duration-100"
          leave-from-class="opacity-100"
          leave-to-class="opacity-0"
        >
          <div v-if="show" :class="toastClasses">
            <div class="flex">
              <div class="flex-shrink-0">
                <i :class="iconClass" class="h-5 w-5"></i>
              </div>
              <div class="ml-3 w-0 flex-1">
                <p class="text-sm font-medium text-gray-900">{{ title }}</p>
                <p v-if="message" class="mt-1 text-sm text-gray-500">{{ message }}</p>
              </div>
              <div class="ml-4 flex-shrink-0 flex">
                <button @click="close" class="bg-white rounded-md inline-flex text-gray-400 hover:text-gray-500 focus:outline-none">
                  <i class="fas fa-times"></i>
                </button>
              </div>
            </div>
          </div>
        </Transition>
      </Teleport>
    `,
    props: {
      show: Boolean,
      title: String,
      message: String,
      variant: {
        type: String,
        default: 'success',
        validator: value => ['success', 'warning', 'error', 'info'].includes(value)
      },
      duration: {
        type: Number,
        default: 5000
      }
    },
    emits: ['close'],
    computed: {
      toastClasses() {
        const baseClasses = 'max-w-sm w-full bg-white shadow-lg rounded-lg pointer-events-auto ring-1 ring-black ring-opacity-5 overflow-hidden';
        return baseClasses;
      },
      iconClass() {
        const icons = {
          success: 'fas fa-check-circle text-green-400',
          warning: 'fas fa-exclamation-triangle text-yellow-400',
          error: 'fas fa-times-circle text-red-400',
          info: 'fas fa-info-circle text-blue-400'
        };
        return icons[this.variant];
      }
    },
    methods: {
      close() {
        this.$emit('close');
      }
    },
    mounted() {
      if (this.duration > 0) {
        setTimeout(() => {
          this.close();
        }, this.duration);
      }
    }
  }
};

// Export for use in Vue app
window.FrappeUI = FrappeUI;
