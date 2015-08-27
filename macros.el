(defun send-current-line-to-shell ()
  (interactive)
  (let ((current-line (buffer-substring-no-properties (line-beginning-position) (line-end-position))))
    (with-current-buffer "*shell*"
      (goto-char (point-max))
      (insert current-line)
      (comint-send-input)
      )
    )
  )

(defun send-current-line-to-gud ()
  (interactive)
  (let ((current-line (buffer-substring-no-properties (line-beginning-position) (line-end-position))))
    (with-current-buffer "*gud*"
      (goto-char (point-max))
      (insert current-line)
      (comint-send-input)
      )
    )
  )