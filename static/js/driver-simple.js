/**
 * Driver Simple - Tour guiado minimalista + UAT Support
 * Implementación propia para reemplazar Driver.js con capacidades UAT
 */

class DriverSimple {
    constructor(options = {}) {
        this.options = {
            opacity: options.opacity || 0.75,
            padding: options.padding || 10,
            animate: false,
            showButtons: options.showButtons !== false,
            nextBtnText: options.nextBtnText || 'Siguiente →',
            prevBtnText: options.prevBtnText || '← Anterior',
            closeBtnText: options.closeBtnText || '×',
            doneBtnText: options.doneBtnText || '¡Listo!',
            allowClose: options.allowClose !== false,
            uatMode: options.uatMode || false
        };
        
        this.steps = [];
        this.currentStep = 0;
        this.isActive = false;
        this.interactionComplete = false;
        this.uatObserverMode = false;
        
        this.overlay = null;
        this.spotlight = null;
        this.popover = null;
        
        // UAT specific properties
        this.uatData = {
            stepStartTime: null,
            stepTimes: [],
            errors: [],
            abandonedSteps: []
        };
        
        this.init();
    }
    
    init() {
        this.createOverlay();
        this.createSpotlight();
        this.createPopover();
        this.bindEvents();
    }
    
    createOverlay() {
        this.overlay = document.createElement('div');
        this.overlay.className = 'driver-overlay';
        this.overlay.style.cssText = `position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0, 0, 0, ${this.options.opacity}); z-index: 9999; display: none;`;
        document.body.appendChild(this.overlay);
    }
    
    createSpotlight() {
        this.spotlight = document.createElement('div');
        this.spotlight.className = 'driver-spotlight';
        this.spotlight.style.cssText = `position: fixed; background: transparent; border: 4px solid #007bff; border-radius: 8px; box-shadow: 0 0 0 9999px rgba(0, 0, 0, ${this.options.opacity}); z-index: 10000; display: none; pointer-events: none;`;
        document.body.appendChild(this.spotlight);
    }
    
    createPopover() {
        this.popover = document.createElement('div');
        this.popover.className = 'driver-popover';
        this.popover.style.cssText = `position: fixed; background: white; border-radius: 12px; box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3); max-width: 320px; z-index: 10001; display: none; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;`;
        
        this.popover.innerHTML = `
            <div class="driver-popover-content" style="padding: 20px;">
                <div class="driver-popover-header">
                    <h3 class="driver-popover-title" style="margin: 0 0 8px 0; font-size: 18px; font-weight: 600; color: #333; line-height: 1.3;"></h3>
                    ${this.options.allowClose ? `<button class="driver-popover-close" style="position: absolute; top: 12px; right: 12px; background: none; border: none; font-size: 24px; color: #666; cursor: pointer; padding: 0; line-height: 1;">${this.options.closeBtnText}</button>` : ''}
                </div>
                <div class="driver-popover-description" style="color: #666; line-height: 1.5; margin-bottom: 20px; font-size: 14px;"></div>
                ${this.options.showButtons ? `
                    <div class="driver-popover-footer" style="display: flex; justify-content: space-between; align-items: center;">
                        <button class="driver-popover-prev" style="background: #f8f9fa; border: 1px solid #dee2e6; padding: 8px 16px; border-radius: 6px; cursor: pointer; font-size: 14px; color: #495057;">${this.options.prevBtnText}</button>
                        <span class="driver-popover-progress" style="font-size: 12px; color: #6c757d; margin: 0 12px;"></span>
                        <button class="driver-popover-next" style="background: #007bff; border: 1px solid #007bff; color: white; padding: 8px 16px; border-radius: 6px; cursor: pointer; font-size: 14px;">${this.options.nextBtnText}</button>
                    </div>
                ` : ''}
            </div>
        `;
        document.body.appendChild(this.popover);
    }
    
    bindEvents() {
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.isActive && this.options.allowClose) this.destroy();
        });
        
        if (this.options.showButtons) {
            const prevBtn = this.popover.querySelector('.driver-popover-prev');
            const nextBtn = this.popover.querySelector('.driver-popover-next');
            
            if (prevBtn) prevBtn.addEventListener('click', () => this.movePrevious());
            if (nextBtn) nextBtn.addEventListener('click', () => this.moveNext());
        }
        
        if (this.options.allowClose) {
            const closeBtn = this.popover.querySelector('.driver-popover-close');
            if (closeBtn) closeBtn.addEventListener('click', () => this.destroy());
        }
        
        this.overlay.addEventListener('click', () => {
            if (this.options.allowClose) this.destroy();
        });
        
        window.addEventListener('popstate', () => {
            if (this.isActive) this.destroy();
        });
    }
    
    /**
     * UAT Observer Mode - Sin UI, solo tracking
     */
    startUATObserver(scenarios = []) {
        this.uatObserverMode = true;
        this.uatData.sessionStart = Date.now();
        this.uatData.scenarios = scenarios;
        
        console.log('UAT Observer Mode iniciado');
        this.setupUATTracking();
        return this;
    }
    
    setupUATTracking() {
        // Tracking de tiempo en cada elemento
        document.addEventListener('mouseover', (e) => {
            if (this.uatObserverMode) {
                this.trackElementHover(e.target);
            }
        });
        
        // Tracking de clicks perdidos (clicks que no llevan a ningún lado)
        document.addEventListener('click', (e) => {
            if (this.uatObserverMode) {
                setTimeout(() => {
                    if (window.location.hash === '' && !e.target.href) {
                        this.trackDeadClick(e.target);
                    }
                }, 100);
            }
        });
        
        // Tracking de scroll behavior
        let scrollTimeout;
        document.addEventListener('scroll', () => {
            if (this.uatObserverMode) {
                clearTimeout(scrollTimeout);
                scrollTimeout = setTimeout(() => {
                    this.trackScrollPattern();
                }, 150);
            }
        });
        
        // Tracking de rage clicks (clicks múltiples rápidos)
        let clickCount = 0;
        let clickTimer;
        document.addEventListener('click', (e) => {
            if (this.uatObserverMode) {
                clickCount++;
                clearTimeout(clickTimer);
                clickTimer = setTimeout(() => {
                    if (clickCount > 3) {
                        this.trackRageClick(e.target, clickCount);
                    }
                    clickCount = 0;
                }, 1000);
            }
        });
    }
    
    trackElementHover(element) {
        // Tracking silencioso de elementos donde el usuario pasa tiempo
        if (!element._hoverStart) {
            element._hoverStart = Date.now();
            
            const hoverEnd = () => {
                const hoverTime = Date.now() - element._hoverStart;
                if (hoverTime > 2000) { // Más de 2 segundos
                    this.uatData.longHovers = this.uatData.longHovers || [];
                    this.uatData.longHovers.push({
                        element: this.getElementSignature(element),
                        time: hoverTime,
                        timestamp: Date.now()
                    });
                }
                delete element._hoverStart;
                element.removeEventListener('mouseleave', hoverEnd);
            };
            
            element.addEventListener('mouseleave', hoverEnd);
        }
    }
    
    trackDeadClick(element) {
        this.uatData.deadClicks = this.uatData.deadClicks || [];
        this.uatData.deadClicks.push({
            element: this.getElementSignature(element),
            timestamp: Date.now()
        });
    }
    
    trackScrollPattern() {
        this.uatData.scrollEvents = this.uatData.scrollEvents || [];
        this.uatData.scrollEvents.push({
            scrollY: window.scrollY,
            timestamp: Date.now()
        });
    }
    
    trackRageClick(element, count) {
        this.uatData.rageClicks = this.uatData.rageClicks || [];
        this.uatData.rageClicks.push({
            element: this.getElementSignature(element),
            clickCount: count,
            timestamp: Date.now()
        });
    }
    
    getElementSignature(element) {
        return {
            tagName: element.tagName,
            id: element.id,
            className: element.className,
            text: element.innerText?.substring(0, 30) || '',
            position: {
                top: element.offsetTop,
                left: element.offsetLeft
            }
        };
    }
    
    getUATData() {
        return {
            ...this.uatData,
            sessionDuration: Date.now() - this.uatData.sessionStart,
            url: window.location.href,
            userAgent: navigator.userAgent
        };
    }
    
    stopUATObserver() {
        this.uatObserverMode = false;
        const data = this.getUATData();
        console.log('UAT Data collected:', data);
        return data;
    }
    
    defineSteps(steps) {
        this.steps = steps.map((step, index) => ({
            ...step,
            index,
            interaction: step.interaction || null
        }));
        return this;
    }
    
    start(stepIndex = 0) {
        if (!this.steps.length) {
            console.warn('Driver Simple: No hay pasos definidos');
            return;
        }
        
        this.currentStep = stepIndex;
        this.isActive = true;
        this.uatData.stepStartTime = Date.now();
        
        this.overlay.style.display = 'block';
        this.showStep(this.currentStep);
        return this;
    }
    
    showStep(stepIndex) {
        if (stepIndex < 0 || stepIndex >= this.steps.length) return;
        
        const step = this.steps[stepIndex];
        let element = typeof step.element === 'string' ? document.querySelector(step.element) : step.element;
        
        // UAT tracking para steps
        if (this.uatData.stepStartTime) {
            const stepTime = Date.now() - this.uatData.stepStartTime;
            this.uatData.stepTimes.push({
                step: stepIndex,
                time: stepTime,
                element: step.element
            });
        }
        
        if (element) {
            this.highlightElement(element, step);
            this.positionPopover(element, step);
        } else {
            this.spotlight.style.display = 'none';
            this.positionPopoverCenter(step);
            
            // UAT: Track missing elements
            this.uatData.errors.push({
                type: 'missing_element',
                step: stepIndex,
                element: step.element,
                timestamp: Date.now()
            });
        }
        
        this.updatePopoverContent(step);
        
        // FIX: Siempre marcar como completo si no hay interacción
        this.interactionComplete = !step.interaction;
        
        this.updateButtons();
        
        if (step.interaction && element) {
            this.setupInteraction(element, step);
        }
        
        if (element) element.scrollIntoView({ behavior: 'smooth', block: 'center', inline: 'center' });
        
        // Reset timer for next step
        this.uatData.stepStartTime = Date.now();
    }
    
    highlightElement(element, step) {
        const rect = element.getBoundingClientRect();
        const padding = this.options.padding;
        
        this.spotlight.style.left = (rect.left - padding) + 'px';
        this.spotlight.style.top = (rect.top - padding) + 'px';
        this.spotlight.style.width = (rect.width + padding * 2) + 'px';
        this.spotlight.style.height = (rect.height + padding * 2) + 'px';
        this.spotlight.style.display = 'block';
    }
    
    positionPopover(element, step) {
        const rect = element.getBoundingClientRect();
        const popoverRect = this.popover.getBoundingClientRect();
        const position = step.popover?.position || 'bottom';
        const spacing = 20;
        
        let left, top;
        switch (position) {
            case 'top': left = rect.left + (rect.width - popoverRect.width) / 2; top = rect.top - popoverRect.height - spacing; break;
            case 'bottom': left = rect.left + (rect.width - popoverRect.width) / 2; top = rect.bottom + spacing; break;
            case 'left': left = rect.left - popoverRect.width - spacing; top = rect.top + (rect.height - popoverRect.height) / 2; break;
            case 'right': left = rect.right + spacing; top = rect.top + (rect.height - popoverRect.height) / 2; break;
            default: left = rect.left + (rect.width - popoverRect.width) / 2; top = rect.bottom + spacing;
        }
        
        left = Math.max(10, Math.min(left, window.innerWidth - popoverRect.width - 10));
        top = Math.max(10, Math.min(top, window.innerHeight - popoverRect.height - 10));
        
        this.popover.style.left = left + 'px';
        this.popover.style.top = top + 'px';
        this.popover.style.transform = 'none';
        this.popover.style.display = 'block';
    }
    
    positionPopoverCenter(step) {
        this.popover.style.left = '50%';
        this.popover.style.top = '50%';
        this.popover.style.transform = 'translate(-50%, -50%)';
        this.popover.style.display = 'block';
    }
    
    updatePopoverContent(step) {
        const title = this.popover.querySelector('.driver-popover-title');
        const description = this.popover.querySelector('.driver-popover-description');
        const progress = this.popover.querySelector('.driver-popover-progress');
        
        if (title && step.popover?.title) {
            title.textContent = step.popover.title;
            title.style.display = 'block';
        } else if (title) title.style.display = 'none';
        
        if (description && step.popover?.description) description.textContent = step.popover.description;
        
        if (progress) progress.textContent = `${this.currentStep + 1} de ${this.steps.length}`;
    }
    
    updateButtons() {
        const prevBtn = this.popover.querySelector('.driver-popover-prev');
        const nextBtn = this.popover.querySelector('.driver-popover-next');
        
        if (prevBtn) prevBtn.style.display = this.currentStep > 0 ? 'block' : 'none';
        
        if (nextBtn) {
            nextBtn.disabled = !this.interactionComplete;
            nextBtn.style.opacity = this.interactionComplete ? '1' : '0.5';
            nextBtn.textContent = this.currentStep >= this.steps.length - 1 ? this.options.doneBtnText : this.options.nextBtnText;
        }
    }
    
    setupInteraction(element, step) {
        const nextBtn = this.popover.querySelector('.driver-popover-next');
        if (nextBtn) {
            nextBtn.disabled = true;
            nextBtn.style.opacity = '0.5';
        }

        const interactionStartTime = Date.now();
        
        const handleInteraction = () => {
            this.interactionComplete = true;
            if (nextBtn) {
                nextBtn.disabled = false;
                nextBtn.style.opacity = '1';
            }
            
            // UAT tracking
            const interactionTime = Date.now() - interactionStartTime;
            this.uatData.interactions = this.uatData.interactions || [];
            this.uatData.interactions.push({
                type: step.interaction.type,
                element: step.element,
                time: interactionTime,
                step: this.currentStep
            });
            
            this.updateButtons();
        };

        const timeoutId = setTimeout(() => {
            if (!this.interactionComplete) {
                this.uatData.abandonedSteps.push({
                    step: this.currentStep,
                    element: step.element,
                    timeSpent: Date.now() - interactionStartTime
                });
            }
        }, 30000); // 30 segundos timeout

        switch (step.interaction.type) {
            case 'click':
                element.addEventListener('click', () => {
                    clearTimeout(timeoutId);
                    handleInteraction();
                }, { once: true });
                break;
            case 'input':
                element.addEventListener('input', (e) => {
                    if (step.interaction.condition && step.interaction.condition(e.target.value)) {
                        clearTimeout(timeoutId);
                        handleInteraction();
                    }
                });
                break;
            case 'submit':
                const form = element.closest('form');
                if (form) {
                    form.addEventListener('submit', (e) => {
                        e.preventDefault();
                        clearTimeout(timeoutId);
                        handleInteraction();
                    }, { once: true });
                }
                break;
        }
    }
    
    moveNext() {
        if (this.interactionComplete) {
            if (this.currentStep < this.steps.length - 1) {
                this.currentStep++;
                this.showStep(this.currentStep);
            } else {
                this.destroy();
            }
        }
    }
    
    movePrevious() {
        if (this.currentStep > 0) {
            this.currentStep--;
            this.showStep(this.currentStep);
        }
    }
    
    destroy() {
        this.isActive = false;
        this.overlay.style.display = 'none';
        this.popover.style.display = 'none';
        this.spotlight.style.display = 'none';
        
        // Final UAT data collection
        if (this.uatData.stepStartTime) {
            const finalStepTime = Date.now() - this.uatData.stepStartTime;
            this.uatData.stepTimes.push({
                step: 'final',
                time: finalStepTime
            });
        }
        
        this.reset();
    }
    
    reset() {
        this.currentStep = 0;
        this.interactionComplete = false;
    }
    
    // Method to get collected UAT data for tours
    getTourUATData() {
        return {
            stepTimes: this.uatData.stepTimes,
            interactions: this.uatData.interactions,
            abandonedSteps: this.uatData.abandonedSteps,
            errors: this.uatData.errors,
            totalTime: this.uatData.stepTimes.reduce((sum, step) => sum + step.time, 0)
        };
    }
}

// Global Driver constructor
window.Driver = function(options) {
    return new DriverSimple(options);
};

window.DriverSimple = DriverSimple;