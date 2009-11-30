;; org-mode
(add-to-list 'load-path "~/elisp/org-mode.git/lisp")
(add-to-list 'load-path "~/elisp/org-mode.git/contrib/lisp")
(require 'org-install)

(custom-set-variables
  ;; custom-set-variables was added by Custom.
  ;; If you edit it by hand, you could mess it up, so be careful.
  ;; Your init file should contain only one such instance.
  ;; If there is more than one, they won't work right.
 '(current-language-environment "UTF-8")
 '(org-export-creator-info nil)
 '(org-export-author-info nil)
 '(org-export-time-stamp-file nil)
 '(org-modules (quote (org-jsinfo org-exp-bibtex org-exp-blocks)))
 '(org-export-html-style-include-default nil)
 '(org-export-html-style "<link rel=\"stylesheet\" type=\"text/css\" href=\"/org.css\" />")
)

