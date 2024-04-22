import reflex as rx

def chevron_down():
    """ Display the chevron down icon.
          
    The chevron down Lucide icon looks slightly different than the Radix one.
    Therefore, the Radix icon is used instead.        
    """
    
    return rx.html(
        '<svg width="9" height="9" viewBox="0 0 9 9" fill="currentColor" '
        'xmlns="http://www.w3.org/2000/svg" class="rt-SelectIcon" '
        'aria-hidden="true">'
        '<path d="M0.135232 3.15803C0.324102 2.95657 0.640521 2.94637 0.841971 '
        '3.13523L4.5 6.56464L8.158 3.13523C8.3595 2.94637 8.6759 2.95657 8.8648 '
        '3.15803C9.0536 3.35949 9.0434 3.67591 8.842 3.86477L4.84197 '
        '7.6148C4.64964 7.7951 4.35036 7.7951 4.15803 7.6148L0.158031 '
        '3.86477C-0.0434285 3.67591 -0.0536285 3.35949 0.135232 3.15803Z">'
        '</path></svg>'
    )